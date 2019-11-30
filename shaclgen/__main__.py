# -*- coding: utf-8 -*-
#!/usr/bin/env python

#%%
from .shaclgen import generate_groups, generate_triples, generate_shacl,generate_merged
import argparse

parser = argparse.ArgumentParser(description="""  
                                 Shacl file generator.
                                 Shaclgen will create a simple shape file by default: 
                                 every class and property will get their own shape.
                                 Nested and extended shape files are possible.""")
    
parser.add_argument("graph", nargs='+',type=str, help="the data graph(s)")
parser.add_argument("serialization", type=str,help="the data graph rdf serialization")
group = parser.add_mutually_exclusive_group()
group.add_argument("-nf", "--nested", action="store_true", help='Property shapes will be nested in nodeshapes iif they occur with one class.')
group.add_argument("-ef", "--extended", action="store_true", help='Expands nested shapes to create individual property shapes for each property, in addition to nesting them when appropriate.')

args = parser.parse_args()
#
#print(args.graph[0])
#print(args.serialization)

def main():
    output = generate_groups(args.graph, args.serialization)
    if args.nested:
        triples = generate_triples(output, 'nf')
    elif args.extended:
        triples = generate_triples(output, 'ef')
    else:
        triples = generate_triples(output, 'sf')

    graph = generate_shacl(triples)
    print(graph)
#
if __name__ == '__main__':
    main()

