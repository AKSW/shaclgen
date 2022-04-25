from rdflib import Graph
from shaclgen.shaclgen import data_graph
from helpers import assertAskQuery


def test_object_class():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:obj_property_iri> <urn:test:other_resource> ;
        <urn:test:obj_property_bnode> [a <urn:test:OtherClassC>] ;
        <urn:test:data_property_int> 4 ;
        <urn:test:data_property_bool> true ;
        <urn:test:data_property_str> "Literal" ;
        <urn:test:data_property_langstr> "Literal"@en .
    <urn:test:other_resource> a <urn:test:OtherClassB> .
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
            sh:property ?obj_property_iri, ?obj_property_bnode, ?data_property_int, ?data_property_bool, ?data_property_langstr, ?data_property_str ;
            sh:targetClass <urn:test:Class> .

        ?obj_property_iri a sh:PropertyShape ;
            sh:class <urn:test:OtherClassB> ;
            sh:nodeKind sh:IRI ;
            sh:path <urn:test:obj_property_iri> .

        ?obj_property_bnode a sh:PropertyShape ;
            #sh:class <urn:test:OtherClassC> ;
            sh:nodeKind sh:BlankNode ;
            sh:path <urn:test:obj_property_bnode> .

        ?data_property_int a sh:PropertyShape ;
            sh:datatype xsd:integer ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_int> .

        ?data_property_bool a sh:PropertyShape ;
            sh:datatype xsd:boolean ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_bool> .

        ?data_property_langstr a sh:PropertyShape ;
            sh:datatype rdf:langString ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_langstr> .

        ?data_property_str a sh:PropertyShape ;
            sh:datatype xsd:string ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_str> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClassB> .

        ?nodeShapeC a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClassC> .
    }
    """,
    )


def test_object_class_iri():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:obj_property_iri> <urn:test:other_resource> .
    <urn:test:other_resource> a <urn:test:OtherClassB> .
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
            sh:property ?obj_property_iri ;
            sh:targetClass <urn:test:Class> .

        ?obj_property_iri a sh:PropertyShape ;
            sh:class <urn:test:OtherClassB> ;
            sh:nodeKind sh:IRI ;
            sh:path <urn:test:obj_property_iri> .

        ?nodeShapeB a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClassB> .
    }
    """,
    )


def test_object_class_bnode():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:obj_property_bnode> [a <urn:test:OtherClassC>] .
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
            sh:property ?obj_property_bnode ;
            sh:targetClass <urn:test:Class> .

        ?obj_property_bnode a sh:PropertyShape ;
            #sh:class <urn:test:OtherClassC> ;
            sh:nodeKind sh:BlankNode ;
            sh:path <urn:test:obj_property_bnode> .

        ?nodeShapeC a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI ;
            sh:targetClass <urn:test:OtherClassC> .
    }
    """,
    )


def test_object_datatype_int():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:data_property_int> 4 .
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
            sh:property ?obj_property_int ;
            sh:targetClass <urn:test:Class> .

        ?data_property_int a sh:PropertyShape ;
            sh:datatype xsd:integer ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_int> .
    }
    """,
    )


def test_object_datatype_bool():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:data_property_bool> true .
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
            sh:property ?data_property_bool ;
            sh:targetClass <urn:test:Class> .

        ?data_property_bool a sh:PropertyShape ;
            sh:datatype xsd:boolean ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_bool> .
    }
    """,
    )


def test_object_datatype_str():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:data_property_str> "Literal"  .
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
            sh:property ?data_property_str ;
            sh:targetClass <urn:test:Class> .

        ?data_property_str a sh:PropertyShape ;
            sh:datatype xsd:string ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_str> .
    }
    """,
    )


def test_object_datatype_langstr():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> ;
        <urn:test:data_property_langstr> "Literal"@en .
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
            sh:property ?data_property_langstr;
            sh:targetClass <urn:test:Class> .

        ?data_property_langstr a sh:PropertyShape ;
            sh:datatype rdf:langString ;
            sh:nodeKind sh:Literal ;
            sh:path <urn:test:data_property_langstr> .
    }
    """,
    )
