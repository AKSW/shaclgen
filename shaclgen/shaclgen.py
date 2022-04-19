from rdflib import Namespace, URIRef, BNode, Literal, Graph
import rdflib
import json
import collections
from rdflib.namespace import XSD, RDF
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

        with open(filepath, "r", encoding="utf-8") as fin:
            self.names = json.load(fin)

        if prefixes:
            with open(prefixes, "r", encoding="utf-8") as fin:
                self.names.update(json.load(fin))

        self.namespaces = []

    def parse_uri(self, URI):
        if "#" in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return label

    def gen_prefix_bindings(self):
        count = 0
        subs = []
        for s, p, o in self.G.triples((None, None, None)):
            subs.append(p)
        for s, p, o in self.G.triples((None, RDF.type, None)):
            subs.append(o)
        subs = list(set(subs))
        for pred in subs:
            if pred.replace(self.parse_uri(pred), "") not in self.names.values():
                count = count + 1
                self.names["ns" + str(count)] = pred.replace(self.parse_uri(pred), "")
        for pref, uri in self.names.items():
            for s in subs:
                if uri == s.replace(self.parse_uri(s), ""):
                    self.namespaces.append((pref, uri))
        self.namespaces = list(set(self.namespaces))

    def sh_label_gen(self, uri):
        parsed = uri.replace(self.parse_uri(uri), "")
        for cur, pref in self.names.items():
            if pref == parsed:
                return cur + "_" + self.parse_uri(uri)

    def uri_validator(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def gen_shape_labels(self, URI):
        if "#" in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return label + "_"

    def extract_classes(self):
        types_query = "select distinct ?class_ { ?s rdf:type ?class_ }"
        for row in self.G.query(types_query, initNs={"rdf": RDF}):
            self.CLASSES[row.class_] = {"label": self.sh_label_gen(row.class_)}

    def extract_props(self):
        self.extract_classes()
        prop = []
        for predicate in self.G.predicates(object=None, subject=None):
            prop.append(predicate)
        props = [
            x
            for x in prop
            if x
            != rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        ]

        for p in sorted(props):
            self.PROPS[p] = {}

        count = 0
        for p in self.PROPS.keys():
            self.PROPS[p]["nodekind"] = None
            self.PROPS[p]["cardinality"] = None

            count = count + 1
            self.PROPS[p]["classes"] = []

            self.PROPS[p]["label"] = self.sh_label_gen(p)
            prop_classes = []

            for sub, pred, obj in self.G.triples((None, p, None)):
                for sub1, pred1, obj1 in self.G.triples((sub, RDF.type, None)):
                    prop_classes.append(obj1)

            uris = []

            [uris.append(x) for x in prop_classes if x not in uris]

            for x in uris:
                self.PROPS[p]["classes"].append(self.CLASSES[x]["label"])

            if len(self.PROPS[p]["classes"]) == 1:
                self.PROPS[p]["type"] = "unique"

            else:
                self.PROPS[p]["type"] = "repeat"

    def extract_contraints(self):
        self.extract_props()

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
        print("## shape file generated by SHACLGEN")
        self.extract_props()
        self.gen_prefix_bindings()
        self.extract_contraints()
        ng = rdflib.Graph()

        SH = Namespace("http://www.w3.org/ns/shacl#")
        ng.bind("sh", SH)

        for x in self.namespaces:
            ng.bind(x[0], x[1])

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
            #
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
                    for objectclass in set(self.PROPS[p]["objectclasses"]):
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
