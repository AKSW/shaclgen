from rdflib import Graph
from shaclgen.shaclgen import data_graph
from helpers import assertAskQuery


def test_namespace():
    source_graph = Graph()

    data = """
    <urn:test:resource> a <urn:test:Class> .
    """

    source_graph.parse(data=data, format="turtle")

    extraction_graph = data_graph(source_graph)
    shacl_graph = extraction_graph.gen_graph(
        namespace=("http://custom.namespace.org/", "custom")
    )

    assertAskQuery(
        shacl_graph,
        """
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    ask {
        ?nodeShape a sh:NodeShape .

        filter regex(str(?nodeShape), "^http://custom.namespace.org/")
    }
    """,
    )
