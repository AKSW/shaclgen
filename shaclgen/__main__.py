#!/usr/bin/env python
from .shaclgen import data_graph
from .schema import schema

import click
from rdflib import Graph
from rdflib.util import guess_format


@click.command()
@click.argument("graphs", nargs=-1, type=str)
@click.option(
    "-o",
    "--ontology",
    help="input file(s) or URL(s) is a schema or ontology",
    default=False,
)
@click.option(
    "-s",
    "--serialization",
    "serial",
    help="result graph serialization, default is turtle. example: -s nt",
    default="turtle",
)
@click.option(
    "-p",
    "--prefixes",
    help="optional declaration of namespace prefixes in a json dictionary.",
    default=None,
)
@click.option(
    "-ns",
    "--namespace",
    type=(str, str),
    help="""
    optional shape namespace declaration.
    example: -ns http://www.example.com exam
    """,
)
@click.option(
    "-i",
    "--implicit",
    "implicit_class_target",
    help="use implicit class targets with RDFS",
    default=False,
)
def main(graphs, ontology, serial, prefixes, namespace, implicit_class_target):
    """
    ---------------------------Shaclgen---------------------------

    Shaclgen takes either a data graph(s) or schema(s) as input and generates
    a basic shape file based on the classes and properties present.

    \b
    usage:
        shaclgen [path or url to graph] [optional arguments]
        $ shaclgen webResource-1-0-0.nt -ns www.example.org exam

    \b
    Multiple graphs:
    To load multiple graphs simply list all the graphs one after the other. The
    RDF serializtion does not matter.
    example:
        $ shaclgen webResource-1-0-0.nt collection-1-0-0.ttl

    \b
    Shape files from data graphs:
    By default, the input graph is processed as instance graph.

    Shape files from ontologies:
    If the input is a schema or ontology (-o), shaclgen will generate
    a nested shape file: properties with rdfs:domain defined in the ontology
    will be nested within the appropriate NodeShape. rdfs:range definitions
    for XML and rdfs datatypes are included.

    \b
    Serialization options:
        turtle = turtle
        ntriples = nt
        rdfxml = xml
        n3 = n3

    """

    source_graph = Graph()

    for graph in graphs:
        source_graph.parse(graph, format=guess_format(graph))

    g = None
    if ontology:
        g = schema(source_graph, prefixes)
    else:
        g = data_graph(source_graph, prefixes)
    g.gen_graph(
        serial=serial, namespace=namespace, implicit_class_target=implicit_class_target
    )


if __name__ == "__main__":
    main()
