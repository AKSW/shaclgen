SHACLGEN
===============

Shaclgen takes either a data graph(s) or schema(s) as input and generates a basic shape file based on the classes and properties present.

**Shape files from data graphs:**
By default, the input graph is processed as a data graph (instance triples). Three formats are possible for data graphs: simple, nested, and extended.

- Simple: Each class and property generate individual Node- and PropertyShapes.

- Nested: Property shapes will be nested in nodeshapes iif they occur with one class.

- Extended: Expands nested shapes to create individual property shapes for each property, in addition to nesting them when appropriate.

**Shape files from ontologies:**
If the input is a schema or ontology, shaclgen generates a nested shape file: properties with rdfs:domain defined in the ontology will be nested within the appropriate NodeShape. rdfs:range definitions for XML and rdfs datatypes are included.

Added support for OWL constructions is planned.

***************




Installation
***************
Using pip:
::

 pip install shaclgen

From source:

https://github.com/alexiskeely/shaclgen


Command line use:
*****************
::

       $ shaclgen graph [optional arguments]

Example usage:
::

  $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/webResource-1-0-0.nt



Command line arguments:
::

  positional arguments:
  graph                 The data graph(s).

::

  optional arguments:
  -h, --help            show this help message and exit
  -nf, --nested         generates a nested shape file
  -ef, --extended       generates an expanded shape file
  -o, --ontology        input file(s) or URL(s) is a schema or ontology
  -s SERIALIZATION, --serialization SERIALIZATION
                        result graph serialization, default is turtle

***************

This project is still in development. Comments, questions, and issues
are welcome!

Contact alexiskm at uw dot edu.
