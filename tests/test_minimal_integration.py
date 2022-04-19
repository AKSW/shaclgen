from rdflib import Graph
from shaclgen.shaclgen import data_graph
from helpers import assertAskQuery


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

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShape a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:Class> ;
            sh:property ?propA, ?propB .

        ?propA a sh:PropertyShape ;
            sh:datatype xsd:string ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:lit_property> .
            ?ropB a sh:PropertyShape ;

            sh:nodeKind sh:IRI ;
            sh:path <urn:test:obj_property> .
    }
    """,
    )


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

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShapeA a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:Class> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClass> .
    }
    """,
    )


def test_object_class():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
    <urn:test:obj_property> <urn:test:other_resource> .
    <urn:test:other_resource> a <urn:test:OtherClass> .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph()

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShapeA a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:property ?property ;
            sh:targetClass <urn:test:Class> .

        ?property a sh:PropertyShape ;
            sh:class <urn:test:OtherClass> ;
            sh:nodeKind sh:IRI ;
            sh:path <urn:test:obj_property> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClass> .
    }
    """,
    )


def test_two_object_classes():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
    <urn:test:obj_property> <urn:test:other_resource> .
    <urn:test:other_resource> a <urn:test:OtherClass>, <urn:test:OtherClass2> .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph()

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShapeA a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:property ?property ;
            sh:targetClass <urn:test:Class> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClass> .

        ?nodeShapeC a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClass2> .

        ?property a sh:PropertyShape ;
            sh:nodeKind sh:IRI ;
            sh:or/rdf:rest*/rdf:first/sh:class <urn:test:OtherClass> ;
            sh:or/rdf:rest*/rdf:first/sh:class <urn:test:OtherClass2> ;
            sh:path <urn:test:obj_property> .
    }
    """,
    )


def test_object_blank_node():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
    <urn:test:obj_property> [] .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph()

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShapeA a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:property ?property ;
            sh:targetClass <urn:test:Class> .

        ?property a sh:PropertyShape ;
            sh:nodeKind sh:BlankNode ;
            sh:path <urn:test:obj_property> .
    }
    """,
    )
