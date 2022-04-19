def assertAskQuery(graph, query):
    result = graph.query(query)
    if not result.askAnswer:
        serialization = graph.serialize(format="turtle")
        explanation = "The actual resulting shacl graph is:\n" + serialization
    assert result.askAnswer, explanation
