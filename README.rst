shaclgen
========

shaclgen generates shacl templates based on the properties and classes
present in a graph. This module uses the rdflib library for working with
rdf.

From the command line:
~~~~~~~~~~~~~~~~~~~~~~

::

    $ shaclgen [uri to data] [serialization]

Supported serializations include: - ``ttl`` for turtle - ``xml`` for
rdf/xml - ``nt`` for ntriples

example:

::

    $ shaclgen https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWebParts/aggregation-1-0-0.ttl ttl

This project is still in development. Comments, questions, and issues
are welcome!

Contact alexiskm at uw dot edu.
