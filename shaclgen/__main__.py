# -*- coding: utf-8 -*-
#!/usr/bin/env python

#%%
import sys
from .shaclgen import generate_groups, generate_triples, generate_shacl

def main():
    input_URI = sys.argv[1:][0]
    serialization = sys.argv[1:][1]
    output = generate_groups(input_URI, serialization)
    triples = generate_triples(output)
    graph = generate_shacl(triples)
    print( graph)

if __name__ == '__main__':
    main()

