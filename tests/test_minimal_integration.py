from rdflib import Graph
from shaclgen.shaclgen import data_graph


def test_create_shape():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
    <urn:test:lit_property> "String" ;
    <urn:test:obj_property> <urn:test:other_resource> .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph()

    print(shacl_graph.serialize(format="turtle"))


def test_two_classes():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> .
    <urn:test:resource_2> a <urn:test:Class> .
    <urn:test:other_resource> a <urn:test:OtherClass> .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph()

    print(shacl_graph.serialize(format="turtle"))
