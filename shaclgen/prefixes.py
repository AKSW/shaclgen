# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Created on Fri Nov  1 09:12:38 2019

@author: alexis
"""
#import json
#count = 0
#def generate_bindings(prefixes):
#    arg_dict = {}
#    with open('namespaces.json','r', encoding='utf-8') as fin:
#        names = json.load(fin)
#    for x,v in names.items():
#        arg_dict['var'+str(count)] = x[1]
#        count = count + 1
#    EX = Namespace('http://www.example.org/')
#        ng.bind('ex', EX)
#    return namespace_d
#        #%%
#        
#
#For x in names.items():    
#    
##%%
#    
#    
#with open('namespaces.json','r', encoding='utf-8') as fin:
#    names = json.load(fin) 
#    
#    
#    
#from rdflib import Graph
#
#G = Graph()
#G.parse('https://trellis.sinopia.io/repository/washington/83337200-3e1f-4a11-8177-de83111d67bc',format='ttl')
#
#subs = []
#for s,p,o in G.triples((None,None,None)):
#    s = s.split('#')
#    subs.append(p)
#for uri in names.values():
#   if uri in subs:
#       print(uri)
#
#from urllib.parse import urlparse
#import urllib
#args = []
#labels = []
#found = []
#
#for y in subs:
#    for pref, uri in names.items():
#        if uri in y:
#            args.append((uri, pref))
#            labels.append((pref,y))
#            found.append(y)          
#args = list(set(args))    
#labels= list(set(labels))
#
#for y in subs:
#    if y not in found:
#        print('missing URI!',y)
#        labels.append(('ex',y))
#labels= list(set(labels))
#
#labels
##%%
#sh_labels = []
#uri_list = list(set(subs))
#prefixes = names.items()
#
#def parse_uri(URI):
#        if '#' in URI:
#            label = URI.split("#")[-1]
#        else:
#            label = URI.split("/")[-1]
#        return label    
#
#nncount = 0
#new_ns = []
#ns_args = []
#
#
#
#
#
#
##%%
#count = 0
#
#        
#            
#for x in uri_list:
#    count = count +1
#    sh_label_gen(x, count)    
#    

#%%
import json
    
with open('namespaces.json','r', encoding='utf-8') as fin:
    names = json.load(fin) 
    
    
    
from rdflib import Graph

G = Graph()
G.parse('https://trellis.sinopia.io/repository/washington/83337200-3e1f-4a11-8177-de83111d67bc',format='ttl')

def parse_uri(URI):
        if '#' in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return label    
    
def gen_prefix_bindings():
    count = 0
    subs = []
    for s,p,o in G.triples((None,None,None)):
        subs.append(p)
    for pred in subs:
        if pred.replace(parse_uri(pred),'') not in names.values():
            count = count +1
            names['ns'+str(count)] = pred.replace(parse_uri(pred),'')
    for pref,uri in names.items():
        for s in subs:
            if uri == s.replace(parse_uri(s),''):
                G.bind(pref,uri)
    return subs

def sh_label_gen(uri):
    match = None
    parsed = uri.replace(parse_uri(uri),'')
    for cur, pref in names.items():
        if pref == parsed:
            return cur+'_'+parse_uri(uri)
    

links = gen_prefix_bindings()
for lin in links:
    print(sh_label_gen(lin))



#%%
names.keys()

#%%
http://id.loc.gov/ontologies/bflc/catalogerID
http://id.loc.gov/ontologies/bflc/catalogerID



#%%
trans = []
for x,v in labels:
    trans.append(v)
from collections import Counter
c = Counter(trans)

#%%
https://www.lib.washington.edu/static/public/cams/data/datasets/uwSemWeb.ttl
    
#%%


for x in labels:
    print(gen_shape_labels(x[1],x[0]))

#%%

print(G.serialize(format='ttl').decode())



#%%

flipped = {}

for key, value in names.items():
    if value not in flipped:
        flipped[value] = [key]
    else:
        flipped[value].append(key)
for k,v in flipped.items():
    if len(v) >1:
        print(k,v)



#potential cleaning needs