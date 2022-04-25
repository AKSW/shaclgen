from loguru import logger
from rdflib import Namespace, URIRef, BNode, Literal, Graph
import rdflib
import json
import collections
from rdflib.namespace import XSD, RDF, RDFS, SH
from rdflib.namespace import NamespaceManager
from urllib.parse import urlparse
import pkg_resources


class data_graph:
    def __init__(self, graph: Graph, prefixes=None):
        self.G = graph

        self.CLASSES = collections.OrderedDict()
        self.PROPS = collections.OrderedDict()
        self.OUT = []

        path = "prefixes/namespaces.json"
        filepath = pkg_resources.resource_filename(__name__, path)

        self.namespaces = NamespaceManager(graph=Graph())
        self.namespaces.bind("sh", SH)

        with open(filepath, "r", encoding="utf-8") as fin:
            for prefix, namespace in json.load(fin).items():
                self.namespaces.bind(prefix, namespace)

        if prefixes:
            with open(prefixes, "r", encoding="utf-8") as fin:
                for prefix, namespace in json.load(fin).items():
                    self.namespaces.bind(prefix, namespace)

    def sh_label_gen(self, uri):
        prefix, namespace, name = self.namespaces.compute_qname(uri)
        return prefix + "_" + name

    def uri_validator(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def extract_classes(self):
        types_query = "select distinct ?class_ { ?s rdf:type ?class_ }"
        for row in self.G.query(types_query, initNs={"rdf": RDF}):
            logger.debug(f"Class: {row.class_}")
            self.CLASSES[row.class_] = {"label": self.sh_label_gen(row.class_)}

    def extract_props(self):
        prop_query = "select distinct ?prop { ?s ?prop ?o . filter(?prop != rdf:type && ?prop != rdfs:label)}"
        for property_row in self.G.query(prop_query, initNs={"rdf": RDF, "rdfs": RDFS}):
            prop = property_row.prop
            logger.debug(f"Property: {prop}")
            self.PROPS[prop] = {
                "nodekind": None,
                "cardinality": None,
                "classes": [],
                "exceptions": [],
                "label": self.sh_label_gen(prop),
            }

            self.extract_props_subj_types(prop)

            if len(self.PROPS[prop]["classes"]) == 1:
                self.PROPS[prop]["type"] = "unique"
            else:
                self.PROPS[prop]["type"] = "repeat"

            self.extract_props_obj_types(prop)

    def extract_props_subj_types(self, prop):
        prop_subject_type = "select distinct ?class_ {{ ?sub {prop} ?o ; a ?class_ . }}"

        try:
            class_property_result = self.G.query(
                prop_subject_type.format(prop=prop.n3())
            )
            for class_row in class_property_result:
                class_ = class_row.class_
                self.PROPS[prop]["classes"].append(self.CLASSES[class_]["label"])
        except Exception as e:
            logger.error(e)
            self.PROPS[prop]["exceptions"].append(
                {"exception": e, "query": prop_subject_type.format(prop=prop.n3())}
            )

    def extract_props_obj_types(self, prop):
        prop_object_type = """
            select distinct ?literal ?dt ?blank ?iri ?class_ {{
                ?s {prop} ?obj .
                optional {{ ?obj a ?class_ }}
                bind(isLiteral(?obj) as ?literal)
                bind(datatype(?obj) as ?dt)
                bind(isBlank(?obj) as ?blank)
                bind(isIRI(?obj) as ?iri)
            }}"""

        try:
            nodekinds = []
            datatypes = []
            objectclasses = []

            property_object_result = self.G.query(
                prop_object_type.format(prop=prop.n3())
            )
            for object_type_row in property_object_result:
                if object_type_row.literal:
                    nodekinds.append("Literal")
                    datatypes.append(object_type_row.dt)
                elif object_type_row.blank:
                    nodekinds.append("BNode")
                elif object_type_row.iri:
                    nodekinds.append("IRI")

                if object_type_row.blank or object_type_row.iri:
                    if object_type_row.class_:
                        objectclasses.append(object_type_row.class_)

            if len(set(nodekinds)) == 1:
                self.PROPS[prop]["nodekind"] = nodekinds[0]
                if nodekinds[0] == "Literal":
                    if len(set(datatypes)) == 1:
                        self.PROPS[prop]["datatype"] = datatypes[0]
                elif nodekinds[0] in ("IRI", "BNode"):
                    self.PROPS[prop]["objectclasses"] = objectclasses
        except Exception as e:
            logger.error(e)
            self.PROPS[prop]["exceptions"].append(
                {"exception": e, "query": prop_object_type.format(prop=prop.n3())}
            )

    def gen_graph(self, namespace=None, implicit_class_target=False):
        logger.info("Start Extraction")
        logger.info("Classes …")
        self.extract_classes()
        logger.info("Properties …")
        self.extract_props()
        logger.info("Write resulting SHACL Graph …")
        ng = rdflib.Graph(namespace_manager=self.namespaces)

        if namespace is not None:
            if self.uri_validator(namespace[0]):
                uri = namespace[0]
                if namespace[0][-1] not in ["#", "/", "\\"]:
                    uri = namespace[0] + "#"
                EX = Namespace(uri)
                ng.bind(namespace[1], EX)
            else:
                print("##malformed URI, using http://example.org/ instead...")
                EX = Namespace("http://www.example.org/")
                ng.bind("ex", EX)
        else:
            EX = Namespace("http://www.example.org/")
            ng.bind("ex", EX)

        for c in self.CLASSES.keys():
            label = self.CLASSES[c]["label"]
            ng.add((EX[label], RDF.type, SH.NodeShape))
            ng.add((EX[label], SH.targetClass, c))
            ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))

        for p in self.PROPS.keys():

            ng.add((EX[self.PROPS[p]["label"]], RDF.type, SH.PropertyShape))
            ng.add((EX[self.PROPS[p]["label"]], SH.path, p))

            for class_prop in self.PROPS[p]["classes"]:
                ng.add((EX[class_prop], SH.property, EX[self.PROPS[p]["label"]]))
            if self.PROPS[p]["nodekind"] == "IRI":
                ng.add((EX[self.PROPS[p]["label"]], SH.nodeKind, SH.IRI))
            elif self.PROPS[p]["nodekind"] == "BNode":
                ng.add((EX[self.PROPS[p]["label"]], SH.nodeKind, SH.BlankNode))
            elif self.PROPS[p]["nodekind"] == "Literal":
                ng.add((EX[self.PROPS[p]["label"]], SH.nodeKind, SH.Literal))
            if (
                "objectclasses" in self.PROPS[p]
                and len(self.PROPS[p]["objectclasses"]) > 0
            ):
                if len(set(self.PROPS[p]["objectclasses"])) == 1:
                    ng.add(
                        (
                            EX[self.PROPS[p]["label"]],
                            SH["class"],
                            self.PROPS[p]["objectclasses"][0],
                        )
                    )
                else:
                    classNum = 0
                    listnode = EX[
                        self.PROPS[p]["label"] + "-classlist-" + str(classNum)
                    ]
                    ng.add((EX[self.PROPS[p]["label"]], SH["or"], listnode))
                    for objectclass in sorted(set(self.PROPS[p]["objectclasses"])):
                        nextlistnode = EX[
                            self.PROPS[p]["label"] + "-classlist-" + str(classNum)
                        ]
                        alternativenode = EX[
                            self.PROPS[p]["label"] + "-class-" + str(classNum)
                        ]
                        if classNum > 0:
                            ng.add((listnode, RDF.rest, nextlistnode))
                        listnode = nextlistnode
                        classNum += 1
                        ng.add((listnode, RDF.first, alternativenode))
                        ng.add((alternativenode, SH["class"], objectclass))
                    ng.add((listnode, RDF.rest, RDF.nil))
            if "datatype" in self.PROPS[p]:
                ng.add(
                    (EX[self.PROPS[p]["label"]], SH.datatype, self.PROPS[p]["datatype"])
                )

        return ng
