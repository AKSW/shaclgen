from rdflib import Graph
from shaclgen.shaclgen import data_graph
from helpers import assertAskQuery


def test_object_class():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:obj_property> <urn:test:other_resource> ;
        <urn:test:data_property_int> 4 ;
        <urn:test:data_property_bool> true ;
        <urn:test:data_property_str> "Literal" ;
        <urn:test:data_property_langstr> "Literal"@en .
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
            sh:property ?obj_property, ?data_property_dt, ?data_property_langstr, ?data_property_str ;
            sh:targetClass <urn:test:Class> .

        ?obj_property a sh:PropertyShape ;
            sh:class <urn:test:OtherClass> ;
            sh:nodeKind sh:IRI ;
            sh:path <urn:test:obj_property> .

        ?data_property_int a sh:PropertyShape ;
            sh:datatype xsd:integer ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_int> .

        ?data_property_bool a sh:PropertyShape ;
            sh:datatype xsd:boolean ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_bool> .

        ?data_property_langstr a sh:PropertyShape ;
            sh:datatype xsd:langString ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_langstr> .

        ?data_property_str a sh:PropertyShape ;
            sh:datatype xsd:string ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_str> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClass> .
    }
    """,
    )
