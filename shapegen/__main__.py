# -*- coding: utf-8 -*-

from rdflib import Graph, Namespace, XSD, RDF, URIRef
from typing import Optional
import requests
import rdflib
import sys


def fetch_uri(uri: str):
    req = requests.get(uri)
    if not req.ok:
        print(req.text)
        return None
    return req.text


def gen_prefixes(input_URI, turtle):
    g = rdflib.Graph()
    g.load(input_URI, format='turtle')
    prop_list = []
    
    for prop in g.predicates(subject=None, object=None):
        prop_list.append(prop)
    prop_list = sorted(list(set(prop_list)))
    
    class_list = []
    for s,p,o in g.triples( (None,  RDF.type, None) ):
       class_list.append(o)
    class_list = sorted(list(set(class_list)))
    
    prefixes = [line for line in turtle.split('\n') if "@prefix" in line]

    pre_binds = []
    for x in prefixes:
        x = x.replace('@prefix', '')
        x = x.replace('>', "")
        x = x.replace('<', "")
        x = x.replace(': ', " ")
        x = x.split(' .')
        x = x[0].split(" ")
        pre_binds.append(x)
    args = []
    for x in pre_binds:
        args.append((x[1], x[-1]))
    return args, class_list, prop_list
    
def generate_triples(class_list, prop_list):
    triples = ""
    ## node shapes
    for x in class_list:
        if '#' in x:
            triples = triples + (f"""
    <http://example.org/{x.split("#")[-1]}Shape> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/shacl#NodeShape> .
    <http://example.org/{x.split("#")[-1]}Shape> <http://www.w3.org/ns/shacl#targetClass> <{x}> .
    
    """)
        else:
            triples = triples + (f"""
    <http://example.org/{x.split("/")[-1]}Shape> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/shacl#NodeShape> .
    <http://example.org/{x.split("/")[-1]}Shape> <http://www.w3.org/ns/shacl#targetClass> <{x}> .
    
    """)
    
    ## property shapes
    for x in prop_list:
        if '#' in x:
            triples = triples +(f"""
    <http://example.org/{x.split("#")[-1]}Shape> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/shacl#PropertyShape> .
    <http://example.org/{x.split("#")[-1]}Shape> <http://www.w3.org/ns/shacl#path> <{x}> .
    
    """)
        else:
            triples = triples +(f"""
    <http://example.org/{x.split("/")[-1]}Shape> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/shacl#PropertyShape> .
    <http://example.org/{x.split("/")[-1]}Shape> <http://www.w3.org/ns/shacl#path> <{x}> .
    
    """)
    return triples
def generate_graph(triples,args):
    g = rdflib.Graph()
    
    ## bind namespaces to graph, adding in example for default shape namespaces and shacl for shacl props/classes.
    for key, uri in args:
        g.bind(key, URIRef(uri))
    g.bind('ex', URIRef('http://example.org/'))
    g.bind('sh', URIRef('http://www.w3.org/ns/shacl#'))
    
    g.parse(data= triples, format='nt')
    shapes = g.serialize(format='turtle')
    shapes = shapes.decode("utf-8") 
    return shapes

def catch_non_ttl(uri):
    if str(uri[-3:]) != 'ttl':
        raise NameError('unsupported file format. Only ttl files accepted at this time')
    else:
        pass

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

