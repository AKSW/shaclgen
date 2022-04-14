SHACLGEN
========

Shaclgen takes either an instance graph/data graph (or multiple graphs) or schema(s) as input and
generates a basic shape file based on the classes and properties
present.

**Shape files from instance data:** By default, the input graph is
processed as a data graph (instance data).

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
    -ns, --namespace      optional shape namespace declaration. ex: http://www.example.com exam
    -i, --implicit        use implicit class targets with RDFS
    -s SERIALIZATION, --serialization SERIALIZATION
                          result graph serialization, default is turtle. example:. -s nt

Serialization options:
        turtle = turtle
        ntriples = nt
        rdfxml = xml
        n3 = n3

Namespace Example usage: :

    $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt -s nt


Namespace argument:
    The namespace argument is takes a full URL and prefix.

Namespace Example usage: :

    $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt -ns http://www.example.org uwlib


* * * * *

This project is still in development. Comments, questions, and issues
are welcome!

Contact alexiskeelie at gmail.com
