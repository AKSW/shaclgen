from rdflib import Namespace, URIRef, BNode, Literal, Graph
import rdflib
import json
import collections
from rdflib.namespace import XSD, RDF, SH
from rdflib.namespace import NamespaceManager
import pkg_resources
from .generator import Generator


class data_graph(Generator):
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


    def extract_classes(self):
        types_query = "select distinct ?class_ { ?s rdf:type ?class_ }"
        for row in self.G.query(types_query, initNs={"rdf": RDF}):
            self.CLASSES[row.class_] = {"label": self.sh_label_gen(row.class_)}

    def extract_props(self):
        prop_query = "select distinct ?prop { ?s ?prop ?o . filter(?prop != rdf:type)}"
        prop_subj_classes = "select distinct ?class_ {{ ?sub {prop} ?o ; a ?class_ . }}"
        for property_row in self.G.query(prop_query, initNs={"rdf": RDF}):
            prop = property_row.prop
            self.PROPS[prop] = {
                "nodekind": None,
                "cardinality": None,
                "classes": [],
                "label": self.sh_label_gen(prop),
            }
            for class_row in self.G.query(prop_subj_classes.format(prop=prop.n3())):
                class_ = class_row.class_
                self.PROPS[prop]["classes"].append(self.CLASSES[class_]["label"])

            if len(self.PROPS[prop]["classes"]) == 1:
                self.PROPS[prop]["type"] = "unique"
            else:
                self.PROPS[prop]["type"] = "repeat"

    def extract_constraints(self):

        for prop in self.PROPS.keys():
            types = []
            classes = []
            datatypes = []
            for s, p, o in self.G.triples((None, prop, None)):
                nodeType = type(o)
                if not types:
                    types.append(nodeType)
                elif nodeType not in types:
                    # currently only one type is handled per property
                    break
                if nodeType == URIRef:
                    for _, _, objectClass in self.G.triples((o, RDF.type, None)):
                        classes.append(objectClass)
                elif nodeType == Literal:
                    datatypes.append(
                        o.datatype or XSD.langString if o.language else XSD.string
                    )

            if len(set(types)) == 1:
                if types[0] == URIRef:
                    self.PROPS[prop]["nodekind"] = "IRI"
                    self.PROPS[prop]["objectclasses"] = classes
                elif types[0] == BNode:
                    self.PROPS[prop]["nodekind"] = "BNode"
                elif types[0] == Literal:
                    self.PROPS[prop]["nodekind"] = "Literal"
                    if len(set(datatypes)) == 1:
                        self.PROPS[prop]["datatype"] = datatypes[0]

    def gen_graph(self, namespace=None, implicit_class_target=False):
        self.extract_classes()
        self.extract_props()
        self.extract_constraints()
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
