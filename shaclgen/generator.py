from rdflib import Graph
from urllib.parse import urlparse


class Generator:
    def __init__(self, graph: Graph, prefixes=None):
        pass

    def sh_label_gen(self, uri):
        prefix, namespace, name = self.namespaces.compute_qname(uri)
        return prefix + "_" + name

    def uri_validator(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def gen_graph(self, namespace=None, implicit_class_target=False):
        pass
