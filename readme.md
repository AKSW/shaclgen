SHACLGEN
========

Shaclgen takes either a data graph(s) or schema(s) as input and
generates a basic shape file based on the classes and properties
present.

**Shape files from instance data:** By default, the input graph is
processed as a instance triples. 

**Shape files from ontologies:** If the input is a schema or ontology,
shaclgen generates a nested shape file: properties with rdfs:domain
defined in the ontology will be nested within the appropriate NodeShape.
rdfs:range definitions for XML and rdfs datatypes are included.

Added support for OWL constructions is planned.

* * * * *

Installation
------------

Using pip: :

    pip install shaclgen

From source:

<https://github.com/alexiskeely/shaclgen>

Command line use:
-----------------

    $ shaclgen [graph] [optional arguments]

Example usage: :

    $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt

Command line arguments: :

    positional arguments:
    graph                 The data graph(s).

    optional arguments:
    -h, --help            show this help message and exit
    -o, --ontology        input file(s) or URL(s) is a schema or ontology
    -ns, --namespace      optional shape namespace declaration
    -s SERIALIZATION, --serialization SERIALIZATION
                          result graph serialization, default is turtle

* * * * *

This project is still in development. Comments, questions, and issues
are welcome!

Contact alexiskeelie at gmail.com
