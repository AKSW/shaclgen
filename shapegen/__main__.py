# -*- coding: utf-8 -*-
#%%
import sys
from .template import catch_non_ttl, fetch_uri, gen_prefixes, generate_triples, generate_graph

def main():
    arg = sys.argv[1:][0]
    catch_non_ttl(arg)
    turtle = fetch_uri(arg)
    args, classes, props = gen_prefixes(arg, turtle)
    triples = generate_triples(classes, props)
    graph = generate_graph(triples, args)
    print( graph)

if __name__ == '__main__':
    main()

