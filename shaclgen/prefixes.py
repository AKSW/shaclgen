# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Created on Fri Nov  1 09:12:38 2019

@author: alexis
"""
#!/usr/bin/env python
prefixes = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix bf: <http://id.loc.gov/ontologies/bibframe/> .
@prefix bflc: <http://id.loc.gov/ontologies/bflc/> .
@prefix bf1: <http://bibframe.org/vocab/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix dpla: <http://dp.la/about/map/> .
@prefix ex: <http://example.org/> .
@prefix edm: <http://www.europeana.eu/schemas/edm/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix http: <http://www.w3.org/2011/http#> .
@prefix ldproc: <https://doi.org/10.6069/uwlib.55.b.2#> .
@prefix library: <http://purl.org/library/> .
@prefix madsrdf: <http://www.loc.gov/mads/rdf/v1#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix plat: <https://doi.org/10.6069/uwlib.55.d.2#> .
@prefix rel: <http://id.loc.gov/vocabulary/relators/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix uwext: <http://faculty.washington.edu/tgis/ld/brumfield/uwDataset/extensions#> .
@prefix uwprop: <https://doi.org/10.6069/uwlib.55.d.3#> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix vra: <http://purl.org/vra/> .
@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> . """

def fetch_uri(uri: str):
    req = requests.get(uri)
    if not req.ok:
        print(req.text)
        return None
    return req.text

def generate_prefixes(prefixes):
    prefixes = [line for line in turtle.split('\n') if "@prefix" in line]
    
    pre_binds = []
    ## processsing to pull out namespaces and URIs
    for x in prefixes:
        x = x.replace('@prefix', '')
        x = x.replace('>', "")
        x = x.replace('<', "")
        x = x.replace(': ', " ")
        x = x.split(' .')
        x = x[0].split(" ")
        pre_binds.append(x)
    
    ## formats the above to be sent to bind method
    args = []
    for x in pre_binds:
        args.append((x[1], x[-1]))