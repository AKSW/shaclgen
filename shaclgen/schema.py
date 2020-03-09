#!/usr/bin/env python

from rdflib import Graph, RDF, RDFS, OWL, Namespace
from rdflib.util import guess_format
from rdflib.namespace import SKOS, DC, DCTERMS, FOAF, DOAP, XSD
from rdflib.term import URIRef, Literal, BNode
import collections, json
from urllib.parse import urlparse
from rdflib.collection import Collection
import pkg_resources

"""
current assumptions: 
    - rdfs:range / unionOf - this is only being used on either all Classes or all Datatypes - is this correct?
    - restrictions on a given property do not require domain or range declaration to be present
        
"""
class schema():
    def __init__(self, args:list):
        self.G = Graph()
        for graph in args:
            self.G.parse(graph,format=guess_format(graph))
        self.CLASSES = collections.OrderedDict()
        self.PROPS = collections.OrderedDict()    
        self.REST = collections.OrderedDict()   
       
        self.namespaces = []
        self.datatypes = [XSD.string, XSD.boolean, XSD.time, XSD.date, XSD.dateTime, XSD.integer, XSD.decimal, 
                          XSD.nonNegativeInteger, XSD.negativeInteger, RDFS.Literal, XSD.positiveInteger, XSD.nonPositiveInteger]
     
        path = 'prefixes/namespaces.json'  
        filepath = pkg_resources.resource_filename(__name__, path)              
        
        with open(filepath,'r', encoding='utf-8') as fin:
            self.names = json.load(fin)

        
    def parse_uri(self, URI):
        if '#' in URI:
            label = URI.split("#")[-1]
        else:
            label = URI.split("/")[-1]
        return str(label)
               
     
    def gen_prefix_bindings(self):
        count = 0
        subs = []
        for s,p,o in self.G.triples((None,RDF.type,None)):
            if type(s) != BNode:
                subs.append(s)
      
        for pred in subs:
            if pred.replace(self.parse_uri(pred),'') not in self.names.values():
                count = count +1
                self.names['ns'+str(count)] = pred.replace(self.parse_uri(pred),'')
        subs = list(set(subs))
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
            self.PROPS[prop]['domain_union']= None
            self.PROPS[prop]['range']= None
            self.PROPS[prop]['range_union']= None
            self.PROPS[prop]['range_value']= None

            self.PROPS[prop]['e_prop'] = None
            self.PROPS[prop]['label'] = self.sh_label_gen(prop)
            self.PROPS[prop]['shape_name'] = None
            self.PROPS[prop]['definition'] = None



#            for domain in self.G.objects(subject=s, predicate=RDFS.domain):
#                if type(domain) != BNode:
#                    self.PROPS[prop]['domain'] = domain
            for sub,pred,ob in self.G.triples((s, RDFS.domain, None)):
                if type(ob) != BNode:
                    self.PROPS[prop]['domain'] = ob
                else:
                    for sub1, pred1, ob1 in self.G.triples((ob, None, None)):

                        if pred1 == OWL.unionOf:
                            c = Collection(self.G,ob1)
                            self.PROPS[prop]['domain_union'] = c
                            
            
            
            for sub,pred,ob in self.G.triples((s, RDFS.range, None)):
                if type(ob) != BNode:
                    self.PROPS[prop]['range'] = ob
                else:
                    for sub1, pred1, ob1 in self.G.triples((ob, None, None)):
                        if pred1 == OWL.oneOf:
                            c = Collection(self.G,ob1)
                            self.PROPS[prop]['range_value'] = c
                        if pred1 == OWL.unionOf:
                            c = Collection(self.G,ob1)
                            self.PROPS[prop]['range_union'] = c
                                                        

            for equal in self.G.objects(subject=s, predicate=OWL.equivalentProperty):
                self.PROPS[prop]['e_prop'] = equal

            for defin in self.G.objects(subject=s, predicate=RDFS.comment):
                self.PROPS[prop]['definition'] = defin
            
            
            for name in self.G.objects(subject=s, predicate=RDFS.label):
        
                self.PROPS[prop]['shape_name'] = name
                if self.PROPS[prop]['shape_name'] == None:
                    self.PROPS[prop]['shape_name'] = self.sh_label_gen(prop)
                    print(self.PROPS[prop]['shape_name'])
            
    
    
    
    def extract_classes(self):    
        self.gen_prefix_bindings()
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
            
        for c in sorted(classes):
            self.CLASSES[c] = {}
        for c in self.CLASSES.keys():
            self.CLASSES[c]['label'] = self.sh_label_gen(c)
            self.CLASSES[c]['definition'] = None    
            s = URIRef(c)           
            for name in self.G.objects(subject=s, predicate=RDFS.label):
                self.CLASSES[c]['shape_name'] = name
                if self.CLASSES[c]['shape_name'] == None:
                    self.CLASSES[c]['shape_name'] = self.sh_label_gen(c)       
            for defin in self.G.objects(subject=s, predicate=RDFS.comment):
                self.CLASSES[c]['definition'] = defin
            
            
    def extract_restrictions(self):

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
            print(rest)
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
            for s,p,o in self.G.triples((rest,OWL.minQualifiedCardinality, None)):
                rest_type.append(p)
                rest_val.append(o)       
            self.REST[rest]['type'] = rest_type[0]
            self.REST[rest]['value'] = rest_val[0]
                
            
    def gen_graph(self, serial='turtle', namespace=None):
        print('dev mode again dummy')
        self.gen_prefix_bindings()
        self.extract_props()
        self.extract_classes()
        self.extract_restrictions()
        ng = Graph()
        SH = Namespace('http://www.w3.org/ns/shacl#')
        ng.bind('sh', SH) 
        
        EX = Namespace('http://www.example.org/')
        ng.bind('ex', EX)
        
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
        
        
        
        
#         add class Node Shapes
        for c in self.CLASSES.keys():
            clabel = self.CLASSES[c]['label']
            ng.add((EX[clabel], RDF.type, SH.NodeShape))
            ng.add((EX[clabel], SH.targetClass, c))
#            ng.add((EX[clabel], SH.name, Literal(self.CLASSES[c]['shape_name']+' Node shape')))
            ng.add((EX[clabel], SH.nodeKind, SH.BlankNodeOrIRI))
            if self.CLASSES[c]['definition'] is not None:
                ng.add((EX[clabel], SH.description, Literal((self.CLASSES[c]['definition']))))
            

        for p in self.PROPS.keys():
            label = self.PROPS[p]['label']
#            ng.add((EX[label], SH.name, Literal(str(self.PROPS[p]['shape_name']) +' Property shape')))
            ng.add((EX[label], RDF.type, SH.PropertyShape))
            ng.add((EX[label], SH.path, p))
            
            
            if self.PROPS[p]['range_value'] is not None:
                rang = self.PROPS[p]['range_value']
                st = BNode()
                ng.add((EX[label], SH['in'], st))
                Collection(ng,st,[Literal(x) for x in rang])

            if self.PROPS[p]['range'] is not None:
                rang = self.PROPS[p]['range']
                if rang in self.datatypes:
                    ng.add((EX[label], SH.datatype, rang))
                
                else:
                    ng.add((EX[label], SH['class'], rang ))
            
            
            ## create range unions using sh:or
            if self.PROPS[p]['range_union'] is not None:
                rang = self.PROPS[p]['range_union']
                if set(rang).issubset(self.datatypes) == True:
                    blan = BNode()
                    listp = []
                    
                    st = BNode(label+str(0)+'a')
                    ng.add((EX[label], EX['or'], st))
                    
                    for x,y in enumerate(rang):
                        if x == 0:
                            ng.add((st, RDF.first, BNode(label+str(x)+'_name') ))
                            ng.add((BNode(label+str(x)+'_name'), SH['class'], y))
                    
                            ng.add((st, RDF.rest, BNode(label+str(x+1)+'a')))
                            
                            
                            
                        else:
                            ng.add((BNode(label+str(x)+'a'), RDF.first, BNode(label+str(x)+'_name') ))
                            ng.add((BNode(label+str(x)+'_name'), SH['class'], y))
                        if x+1 ==len(rang):
                            ng.add((BNode(label+str(x)+'a'), RDF.rest, RDF.nil))
                        else:
                            ng.add((BNode(label+str(x)+'a'), RDF.rest, BNode(label+str(x+1)+'a')))
               
                else:
               
                    
                    st = BNode(label+str(0)+'a')
                    ng.add((EX[label], EX['or'], st))
                    
                    for x,y in enumerate(rang):
                        if x == 0:
                            ng.add((st, RDF.first, BNode(label+str(x)+'_name') ))
                            ng.add((BNode(label+str(x)+'_name'), SH['class'], y))
                    
                            ng.add((st, RDF.rest, BNode(label+str(x+1)+'a')))
                            
                            
                            
                        else:
                            ng.add((BNode(label+str(x)+'a'), RDF.first, BNode(label+str(x)+'_name') ))
                            ng.add((BNode(label+str(x)+'_name'), SH['class'], y))
                        if x+1 ==len(rang):
                            ng.add((BNode(label+str(x)+'a'), RDF.rest, RDF.nil))
                        else:
                            ng.add((BNode(label+str(x)+'a'), RDF.rest, BNode(label+str(x+1)+'a')))

           
            
            
            
            
            
            if self.PROPS[p]['definition'] is not None:
                ng.add((EX[label], SH.description, Literal((self.PROPS[p]['definition']))))
            
            
            if self.PROPS[p]['domain'] is not None:         
                if self.PROPS[p]['domain'] in self.CLASSES.keys():
                    dlabel = self.CLASSES[self.PROPS[p]['domain']]['label']
                    plabel = self.PROPS[p]['label']#
                    ng.add((EX[dlabel], SH.property, EX[plabel]))
            
            if self.PROPS[p]['domain_union'] is not None:         
                for d in self.PROPS[p]['domain_union']:
                    if d in self.CLASSES.keys():
                        dlabel = self.CLASSES[d]['label']
                        plabel = self.PROPS[p]['label']#
                        ng.add((EX[dlabel], SH.property, EX[plabel]))
        
        for r in self.REST.keys():
            blank = BNode()

#                if self.REST[r]['onProp'] == p: #and self.REST[r]['onClass'] == self.PROPS[p]['domain']:
                    
            ng.add((EX[self.sh_label_gen(self.REST[r]['onClass'])], SH.property, blank ))
            ng.add((blank, SH.path, self.REST[r]['onProp'] ))
            if self.REST[r]['type'] in (OWL.cardinality):
                        
                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
            elif self.REST[r]['type'] in (OWL.minCardinality):
                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
            elif self.REST[r]['type'] in (OWL.maxCardinality):
                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
            elif self.REST[r]['type'] in (OWL.allValuesFrom):
                ng.add((blank, SH['class'], self.REST[r]['value']))
            elif self.REST[r]['type'] in (OWL.someValuesFrom):
                ng.add((blank, SH['qualifiedMinCount'], Literal(1, datatype=XSD.integer)))
                ng.add((blank, SH['qualifiedValueShape'], BNode('count'+str(rest)) ))               
                ng.add((BNode('count'+str(rest)), SH['class'], self.REST[r]['value'] ))
            else:
                pass
                   
                    
                  
                    
#            for r in self.REST.keys():
#                blank = BNode()
#
#                if self.REST[r]['onProp'] == p: #and self.REST[r]['onClass'] == self.PROPS[p]['domain']:
#                    
#                    ng.add((EX[self.sh_label_gen(self.PROPS[p]['domain'])], SH.property, blank ))
#                    ng.add((blank, SH.path, p ))
#                    if self.REST[r]['type'] in (OWL.cardinality):
#                        
#                        ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                        ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                    elif self.REST[r]['type'] in (OWL.minCardinality):
#                        ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                    elif self.REST[r]['type'] in (OWL.maxCardinality):
#                        ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                    else:
#                        pass
#                   
#                    
#                    
#                    
#                    ng.add((blank, SH.name, Literal(self.PROPS[p]['shape_name'] +' Property shape')))
#                    ng.add((blank, SH.path, p))
#                    if self.PROPS[p]['definition'] is not None:
#                        ng.add((blank, SH.description, Literal((self.PROPS[p]['definition']))))
#
#                    if self.PROPS[p]['range'] is not None:
#                        rang = self.PROPS[p]['range']
#                        if rang in self.datatypes:
#                            ng.add((blank, SH.datatype, rang))
#                        else:
#                            ng.add((blank, SH['class'], rang ))
#                    for r in self.REST.keys():
#                        if self.REST[r]['onProp'] == p and self.REST[r]['onClass'] == self.PROPS[p]['domain']:
#                            if self.REST[r]['type'] in (OWL.cardinality):
#                                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                            elif self.REST[r]['type'] in (OWL.minCardinality):
#                                ng.add((blank, SH.minCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                            elif self.REST[r]['type'] in (OWL.maxCardinality):
#                                ng.add((blank, SH.maxCount, Literal(self.REST[r]['value'], datatype=XSD.integer)))
#                            else:
#                                pass
#                        else:
#                            pass
#                else:
#                    label = self.PROPS[p]['label']
#                    ng.add((EX[label], RDF.type, SH.NodeShape))
#                    ng.add((EX[label], SH.name, Literal(self.PROPS[p]['shape_name'] +' Property shape')))
#                    ng.add((EX[label], SH.targetSubjectsOf, p))
#                    ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))
#                    ng.add((EX[label], SH.property, blank))
#                    ng.add((blank, SH.path, p))
#                    if self.PROPS[p]['range'] is not None:
#                            rang = self.PROPS[p]['range']
#                            if rang in self.datatypes:
#                                ng.add((blank, SH.datatype, rang))
#                            else:
#                                ng.add((blank, SH['class'], rang ))
#            else:
#                blank = BNode()
#                label = self.PROPS[p]['label']
#                ng.add((EX[label], SH.name, Literal(self.PROPS[p]['shape_name'] +' Property shape')))
#                ng.add((EX[label], RDF.type, SH.NodeShape))
#                ng.add((EX[label], SH.targetSubjectsOf, p))
#                ng.add((EX[label], SH.nodeKind, SH.BlankNodeOrIRI))
#                ng.add((EX[label], SH.property, blank))
#                ng.add((blank, SH.path, p))
#                if self.PROPS[p]['range'] is not None:
#                        rang = self.PROPS[p]['range']
#                        if rang in self.datatypes:
#                            ng.add((blank, SH.datatype, rang))
#                        else:
#                            ng.add((blank, SH['class'], rang ))
        
        print(ng.serialize(format='ttl').decode())        
