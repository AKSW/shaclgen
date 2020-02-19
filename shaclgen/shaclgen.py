#!/usr/bin/env python


from rdflib import Graph, Namespace,  URIRef, BNode
import rdflib, json
from collections import Counter
from rdflib.util import guess_format
import collections
from rdflib.namespace import XSD, RDF, OWL, RDFS
from urllib.parse import urlparse


class data_graph():
    def __init__(self, args:list):
        self.G = rdflib.Graph()
        
        for graph in args:
            self.G.parse(graph,format=guess_format(graph))
        
        self.CLASSES = collections.OrderedDict()
        self.PROPS = collections.OrderedDict()
        self.OUT = []
        with open('shaclgen/namespaces.json','r', encoding='utf-8') as fin:
            self.names = json.load(fin)
        self.namespaces = []
              
#    def extract_pairs(self):
#         
#        classes = []
#        for s,p,o in self.G.triples( (None,  RDF.type, None) ):
#            classes.append(o)
#        
#        classes = sorted(list(set(classes)))
#    
#        tupes = []
#        count = 0
#        for clas in classes:
#            count = count +1
#            for s,p,o in self.G.triples((None, RDF.type, clas)):
#                for s,p1,o1 in self.G.triples((s, None, None)):
#                    tupes.append((count,clas,p1))
#        
#        tupes = list(set(tupes))
#    
#        tupes = [x for x in tupes if x[2] != rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')]
#
#        c = Counter(x[2] for x in tupes)
#        self.OUT = [x + ('unique',) if c[x[2]] == 1 else x + ('repeat',) for x in tupes]
#        print(self.OUT)
        
        

    
    def parse_uri(self, URI):
        if '#' in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return label       
                
        
    def gen_prefix_bindings(self):
        count = 0
        subs = []
        for s,p,o in self.G.triples((None,None,None)):
            subs.append(p)
        for pred in subs:
            if pred.replace(self.parse_uri(pred),'') not in self.names.values():
                count = count +1
                self.names['ns'+str(count)] = pred.replace(self.parse_uri(pred),'')
        for pref,uri in self.names.items():
            for s in subs:
                if uri == s.replace(self.parse_uri(s),''):
                    self.namespaces.append((pref,uri))
        self.namespaces = list(set(self.namespaces))

    def sh_label_gen(self,uri):
        parsed = uri.replace(self.parse_uri(uri),'')
        for cur, pref in self.names.items():
            if pref == parsed:
                return cur+'_'+self.parse_uri(uri)
                
    def uri_validator(self,x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False





    def gen_shape_labels(self, URI):
        if '#' in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return label+'_'

    def extract_classes(self):
        classes = []
        for s,p,o in self.G.triples((None, RDF.type, None)):
            classes.append(o)
            
        for c in sorted(classes):
            self.CLASSES[c] = {}
        count = 0    

        for class_item in self.CLASSES.keys():
            count = count +1
            self.CLASSES[class_item]['label'] = self.sh_label_gen(class_item)



    def extract_props(self):
        self.extract_classes()
        prop = []
        for predicate in self.G.predicates(object=None, subject=None):
            prop.append(predicate)
        props = [x for x in prop if x != rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')]

        for p in sorted(props):
            self.PROPS[p] = {}
        
        count = 0
        for p in self.PROPS.keys():
            count = count +1
            self.PROPS[p]['classes']=[]
        
            self.PROPS[p]['label'] = self.sh_label_gen(p)
            prop_classes = []
            
            for sub,pred,obj in self.G.triples((None, p, None)):
                for sub1, pred1, obj1 in self.G.triples( (sub, RDF.type, None) ):
                    prop_classes.append(obj1)
            
            uris = []

            [uris.append(x) for x in prop_classes if x not in uris] 

            for x in uris:
                self.PROPS[p]['classes'].append(self.CLASSES[x]['label'])
            
            if len(self.PROPS[p]['classes']) == 1:
                self.PROPS[p]['type'] = 'unique'

            else:
                self.PROPS[p]['type'] = 'repeat'
        
   
    
    def gen_graph(self, serial='turtle', graph_format=None, namespace=None):
        self.extract_props()
        self.gen_prefix_bindings()

        ng = rdflib.Graph()
        
        SH = Namespace('http://www.w3.org/ns/shacl#')
        ng.bind('sh', SH) 
        
        for x in self.namespaces:
            ng.bind(x[0],x[1])
        
        if namespace != None:
            if self.uri_validator(namespace[0]) != False:
                uri = namespace[0]
                if namespace[0][-1] not in ['#','/','\\']:
                    uri = namespace[0]+'/'
                EX = Namespace(uri)
                ng.bind(namespace[1], EX)
            else:
                print('##malformed URI, using http://example.org/ instead...')
                EX = Namespace('http://www.example.org/')
                ng.bind('ex', EX)
        else: 
            EX = Namespace('http://www.example.org/')
            ng.bind('ex', EX)
        
        for c in self.CLASSES.keys():
            label = self.CLASSES[c]['label']
            ng.add((EX[label],RDF.type, SH.NodeShape ))
            ng.add( (EX[label], SH.targetClass, c) )
            ng.add( (EX[label], SH.nodeKind, SH.BlankNodeOrIRI) )    
            
        for p in self.PROPS.keys():
            if graph_format == 'nf' or graph_format == 'ef':

                if self.PROPS[p]['type'] == 'unique':
                    blank = BNode()
                    ng.add( (EX[self.PROPS[p]['classes'][0]], SH.property, blank) )
                    ng.add( (blank, SH.path, p))
 
                    if graph_format =='ef':
                        ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                        ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
                    else:
                        pass
                       
                else:
                    for class_prop in self.PROPS[p]['classes']:
                        ng.add( (EX[class_prop], SH.property, EX[self.PROPS[p]['label']]) )
                    ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                    ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
           
            else:
                ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
                ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
#                
            for class_prop in self.PROPS[p]['classes']:
                ng.add( (EX[class_prop], SH.property, EX[self.PROPS[p]['label']]) )

            
        print(ng.serialize(format=serial).decode())
 