#!/usr/bin/env python


from rdflib import Graph, Namespace,  URIRef, BNode
import rdflib
from collections import Counter
from rdflib.util import guess_format
import collections
from rdflib.namespace import XSD, RDF, OWL, RDFS


class data_graph():
    def __init__(self, args:list):
        self.G = rdflib.Graph()
        
        for graph in args:
            self.G.parse(graph,format=guess_format(graph))
        
        self.CLASSES = collections.OrderedDict()
        self.PROPS = collections.OrderedDict()
        self.OUT = []
        
        
    def extract_pairs(self):
         
        classes = []
        for s,p,o in self.G.triples( (None,  RDF.type, None) ):
            classes.append(o)
        
        classes = sorted(list(set(classes)))
    
        tupes = []
        count = 0
        for clas in classes:
            count = count +1
            for s,p,o in self.G.triples((None, RDF.type, clas)):
                for s,p1,o1 in self.G.triples((s, None, None)):
                    tupes.append((count,clas,p1))
        
        tupes = list(set(tupes))
    
        tupes = [x for x in tupes if x[2] != rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')]

        c = Counter(x[2] for x in tupes)
        self.OUT = [x + ('unique',) if c[x[2]] == 1 else x + ('repeat',) for x in tupes]
        print(self.OUT)

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
        for clas in self.CLASSES.keys():
            count = count +1
            self.CLASSES[clas]['label'] = self.gen_shape_labels(clas)+str(count)



    def extract_props(self):
        self.extract_classes()
        props = []
        for predicate in self.G.predicates(object=None, subject=None):
            props.append(predicate)
        props = [x for x in props if x != rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')]

        for p in sorted(props):
            self.PROPS[p] = {}
        
        count = 0
        for p in self.PROPS.keys():
            count = count +1
            self.PROPS[p]['classes']=[]
        
            self.PROPS[p]['label'] = self.gen_shape_labels(p)+str(count)
            prop_classes = []
            for sub,pred,obj in self.G.triples((None, p, None)):
                for sub, pred1, obj1 in self.G.triples( (sub, RDF.type, None) ):
                    prop_classes.append(obj1)
            
            uris = []

            [uris.append(x) for x in prop_classes if x not in uris] 

            for x in uris:
                self.PROPS[p]['classes'].append(self.CLASSES[x]['label'])
            
            if len(self.PROPS[p]['classes']) == 1:
                self.PROPS[p]['type'] = 'unique'

            else:
                self.PROPS[p]['type'] = 'repeat'
        
    
    
    
    def gen_graph(self, serial='turtle', graph_format=None):
        self.extract_props()
        
        ng = rdflib.Graph()
        
        SH = Namespace('http://www.w3.org/ns/shacl#')
        ng.bind('sh', SH) 
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
                    ng.add( (EX[self.PROPS[p]['classes'][0]], SH.property, EX[self.PROPS[p]['label']]) )
                    ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                    ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
           
            else:
                ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
                ng.add( (EX[self.PROPS[p]['classes'][0]], SH.property, EX[self.PROPS[p]['label']]) )
                ng.add( (EX[self.PROPS[p]['label']], RDF.type, SH.PropertyShape) )
                ng.add( (EX[self.PROPS[p]['label']], SH.path, p) )
            
        print(ng.serialize(format=serial).decode())
 
