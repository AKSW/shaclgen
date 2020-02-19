#!/usr/bin/env python

from rdflib import Graph, RDF, RDFS, OWL, Namespace
from rdflib.util import guess_format
from rdflib.namespace import SKOS, DC, DCTERMS, FOAF, DOAP, XSD
from rdflib.term import URIRef, Literal, BNode
import collections, json
from urllib.parse import urlparse


class schema():
    def __init__(self, args:list):
        self.G = Graph()
        for graph in args:
            self.G.parse(graph,format=guess_format(graph))
        self.CLASSES = collections.OrderedDict()
        self.PROPS = collections.OrderedDict()    
        self.REST = collections.OrderedDict()   
        with open('shaclgen/namespaces.json','r', encoding='utf-8') as fin:
            self.names = json.load(fin)
        self.namespaces = []
        self.datatypes = [XSD.string, XSD.boolean, XSD.time, XSD.date, XSD.dateTime, XSD.integer, XSD.decimal, 
                          XSD.nonNegativeInteger, XSD.negativeInteger, RDFS.Literal, XSD.positiveInteger, XSD.nonPositiveInteger]
     
        
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
        
   
    def extract_props(self):    
        properties = []
        
        #gather properties
        for s,p,o in self.G.triples((None,RDF.type,OWL.DatatypeProperty)):
            properties.append(s)
        
        for s,p,o in self.G.triples((None,RDF.type,OWL.ObjectProperty)):
            properties.append(s)
        for s,p,o in self.G.triples((None,RDF.type,OWL.AnnotationProperty)):
            properties.append(s)
        for s,p,o in self.G.triples((None,RDF.type,OWL.TransitiveProperty)):
            properties.append(s)
       
        for s,p,o in self.G.triples((None,RDF.type,RDF.Property)):
            properties.append(s)
        
        for p in sorted(properties):
            self.PROPS[p] = {}
       
        
        #gather property values
        count = 0
        for prop in self.PROPS.keys():
            count = count + 1
            s = URIRef(prop)           
            self.PROPS[prop]['domain']= None
            self.PROPS[prop]['range']= None
            self.PROPS[prop]['e_prop'] = None
            self.PROPS[prop]['label'] = self.sh_label_gen(prop)

            for domain in self.G.objects(subject=s, predicate=RDFS.domain):
                if type(domain) != BNode:
                    self.PROPS[prop]['domain'] = domain
               
            for ranges in self.G.objects(subject=s, predicate=RDFS.range):
                if type(ranges) != BNode:
                    self.PROPS[prop]['range'] = ranges

            for equal in self.G.objects(subject=s, predicate=OWL.equivalentProperty):
                self.PROPS[prop]['e_prop'] = equal
            
            
    
    
    
    def extract_classes(self):    
        classes = []
        for s,p,o in self.G.triples((None,RDF.type,OWL.Class)):
            if type(s) != BNode:
                classes.append(s)
            else:
                pass
        for s,p,o in self.G.triples((None,RDF.type,RDFS.Class)):
            if type(s) != BNode:
                classes.append(s)
            else:
                pass
            
        count = 0    
        for c in sorted(classes):
            self.CLASSES[c] = {}
        for c in self.CLASSES.keys():
            count = count +1
            self.CLASSES[c]['label'] = self.sh_label_gen(c)
            
            
            
            
    def extract_restrictions(self):
        # does not handle nested restrictions within other class descriptions
        
        restrictions = []
        for s,p,o in self.G.triples((None, OWL.onProperty, None)):
            restriction = s
            for s in self.G.subjects(object=restriction, predicate=None):
                if type(s) != BNode:
                    for o in self.G.objects(subject=restriction, predicate=OWL.onProperty): 
                        if type(o) != BNode:    
                            restrictions.append(restriction)
        for r in sorted(restrictions):
            self.REST[r] = {}
        
        for rest in self.REST.keys():  
            for o in self.G.objects(subject=rest, predicate=OWL.onProperty):
                self.REST[rest]['onProp']= o
           
            for s in self.G.subjects(object=rest, predicate=None):
                self.REST[rest]['onClass']= s
                
            rest_type = []
            rest_val =[]
            for s,p,o in self.G.triples((rest,OWL.maxCardinality,None)):
                rest_type.append(p)
                rest_val.append(o)
            for p in self.G.triples((rest,OWL.minCardinality, None)):
                rest_type.append(p)
                rest_val.append(o)
            for s,p,o in self.G.triples((rest, OWL.cardinality, None)):
                rest_type.append(p)
                rest_val.append(o)        
            for s,p,o in self.G.triples((rest,OWL.allValuesFrom,None)):
                rest_type.append(p)
                rest_val.append(o)
            for s,p,o in self.G.triples((rest,OWL.someValuesFrom, None)):
                rest_type.append(p)
                rest_val.append(o)            
            for s,p,o in self.G.triples((rest,OWL.hasValue, None)):
                rest_type.append(p)
                rest_val.append(o)                
            self.REST[rest]['type'] = rest_type[0]
            self.REST[rest]['value'] = rest_val[0]
                
            
    def gen_graph(self, serial='turtle', namespace=None):

        self.extract_props()
        self.extract_classes()
        self.extract_restrictions()
        ng = Graph()
        SH = Namespace('http://www.w3.org/ns/shacl#')
        ng.bind('sh', SH) 
        
#        EX = Namespace('http://www.example.org/')
#        ng.bind('ex', EX)
        
        if namespace != None:
            print(namespace)
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
        
        
        
        
        # add class Node Shapes
        for c in self.CLASSES.keys():
            label = self.CLASSES[c]['label']
            ng.add((EX[label], RDF.type, SH.NodeShape))
            ng.add((EX[label], SH.targetClass, c))
            ng.add((EX[label], SH.name, Literal(label+' Node shape')))

            ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))
        for p in self.PROPS.keys():
            if self.PROPS[p]['domain'] is not None:
                blank = BNode()
                if self.PROPS[p]['domain'] in self.CLASSES.keys():
                    label = self.CLASSES[self.PROPS[p]['domain']]['label']
                    ng.add((EX[label], SH.property, blank))
                    ng.add((EX[label], SH.name, Literal(label+' Property shape')))

                    ng.add((blank, SH.path, p))
                    if self.PROPS[p]['range'] is not None:
                        rang = self.PROPS[p]['range']
                        if rang in self.datatypes:
                            ng.add((blank, SH.datatype, rang))
                        else:
                            ng.add((blank, SH['class'], rang ))
                    for r in self.REST.keys():
                        if self.REST[r]['onProp'] == p and self.REST[r]['onClass'] == self.PROPS[p]['domain']:
                            if self.REST[r]['type'] in (OWL.cardinality):
                                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
                                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
                            elif self.REST[r]['type'] in (OWL.minCardinality):
                                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
                            elif self.REST[r]['type'] in (OWL.maxCardinality):
                                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
                            else:
                                pass
                        else:
                            pass
                else:
                    label = self.PROPS[p]['label']
                    ng.add((EX[label], RDF.type, SH.NodeShape))
                    ng.add((EX[label], SH.name, Literal(label+' Property shape')))

                    ng.add((EX[label], SH.targetSubjectsOf, p))
                    ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))
                    ng.add((EX[label], SH.property, blank))
                    ng.add((blank, SH.path, p))
                    if self.PROPS[p]['range'] is not None:
                            rang = self.PROPS[p]['range']
                            if rang in self.datatypes:
                                ng.add((blank, SH.datatype, rang))
                            else:
                                ng.add((blank, SH['class'], rang ))
            else:
                blank = BNode()
                label = self.PROPS[p]['label']
                ng.add((EX[label], SH.name, Literal(label+' Property shape')))

                ng.add((EX[label], RDF.type, SH.NodeShape))
                ng.add((EX[label], SH.targetSubjectsOf, p))
                ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))
                ng.add((EX[label], SH.property, blank))
                ng.add((blank, SH.path, p))
                if self.PROPS[p]['range'] is not None:
                        rang = self.PROPS[p]['range']
                        if rang in self.datatypes:
                            ng.add((blank, SH.datatype, rang))
                        else:
                            ng.add((blank, SH['class'], rang ))
        
        print(ng.serialize(format=serial).decode())        



     