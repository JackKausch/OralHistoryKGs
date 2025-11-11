import os
import openai
import re
from PyPDF2 import PdfReader

openai.api_key_path= './key.txt'

pdf_dir = "./Sammet"
output_dir = "./SammetRDF2"
os.makedirs(output_dir, exist_ok=True)

data_model_prompt = """
You are an RDF converter. 
Given the text of a document, extract key entities and relationships 
according to the Factoid Prosopography Ontology (FPO). 

@prefix : <https://github.com/johnBradley501/FPO/raw/master/fpo.owl#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix cidoc: <http://erlangen-crm.org/current/> .
@prefix frbroo: <http://www.ifla.org/files/assets/cataloguing/FRBRoo/frbroo_v_2.4.pdf#> .
@base <https://github.com/johnBradley501/FPO/raw/master/fpo.owl> .

<https://github.com/johnBradley501/FPO/raw/master/fpo.owl> rdf:type owl:Ontology ;
                                                            dc:creator "John Bradley (King's Digital Lab, King's Collage London)" ;
                                                            dc:rights "Creative Commons Attribution-NonCommercial 4.0 International License." ;
                                                            dc:title "A Factoid Prosopography Ontology" ;
                                                            rdfs:comment FPO (Factoid Prosopography Ontology) is an ontology which has been defined to formalise some aspects of the practice of Factoid Prosopography as it has been practiced in the six structured prosopographies collaboratively created by King's College London's Department of Digital Humanities (formally Centre for Computing in the Humanities) with various historians between 1995 and 2016.  By defining this ontology its makers wish to clarify some aspects of how this approach for factoid prosopography actually worked.

It was first created (version 0.1) in 2016 by John Bradley, now a retired member of DDH but who participated in various ways (from developer to Co-Investigator) in all six of KCL's factoid prosopographical projects.  This version (1.0: June 2010) of FPO is much like the previous preliminary version, with the most significant change being in the representation of :Reference and the associated addition of the new class :Role. ;
                                                            rdfs:label "A Factoid Prosopography Ontology" ;
                                                            owl:versionInfo 1.0 .

#################################################################
#    Annotation properties
#################################################################

###  http://purl.org/dc/elements/1.1/creator
dc:creator rdf:type owl:AnnotationProperty .


###  http://purl.org/dc/elements/1.1/rights
dc:rights rdf:type owl:AnnotationProperty .


###  http://purl.org/dc/elements/1.1/title
dc:title rdf:type owl:AnnotationProperty .


#################################################################
#    Object Properties
#################################################################

  #  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#assertsPossessionOf
:assertsPossessionOf rdf:type owl:ObjectProperty ;
                     rdfs:domain :PossessionFactoid ;
                     rdfs:range :Possession .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#dateAsserted
:dateAsserted rdf:type owl:ObjectProperty ;
              rdfs:domain :Factoid ;
              rdfs:range :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#dateForAssertion
:dateForAssertion rdf:type owl:ObjectProperty ;
                  rdfs:domain :StateOfAffairsFactoid ;
                  rdfs:range :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#fromSource
:fromSource rdf:type owl:ObjectProperty ;
            rdfs:domain :SourceCitation ;
            rdfs:range :Source .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasDateAssertionMade
:hasDateAssertionMade rdf:type owl:ObjectProperty ;
                      rdfs:domain :Assertion ;
                      rdfs:range :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasFromRange
:hasFromRange rdf:type owl:ObjectProperty ;
              rdfs:domain :DateRangeCompound ;
              rdfs:range :DateRangeTEI .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasLifeDates
:hasLifeDates rdf:type owl:ObjectProperty ;
              rdfs:domain :Person ;
              rdfs:range :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasReference
:hasReference rdf:type owl:ObjectProperty ;
              rdfs:domain :Assertion ;
              rdfs:range :Reference .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasRole
:hasRole rdf:type owl:ObjectProperty ;
         rdfs:domain :Reference ;
         rdfs:range :Role .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasToRange
:hasToRange rdf:type owl:ObjectProperty ;
            rdfs:domain :DateRangeCompound ;
            rdfs:range :DateRangeTEI .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#involvesPossession
:involvesPossession rdf:type owl:ObjectProperty ;
                    rdfs:domain :Transaction ;
                    rdfs:range :Possession .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#isFrom
:isFrom rdf:type owl:ObjectProperty ;
        rdfs:domain :DateRangeTEI ;
        rdfs:range :Date .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#isNotAfter
:isNotAfter rdf:type owl:ObjectProperty ;
            rdfs:domain :DateRangeTEI ;
            rdfs:range :Date .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#isNotBefore
:isNotBefore rdf:type owl:ObjectProperty ;
             rdfs:domain :DateRangeTEI ;
             rdfs:range :Date .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#isTo
:isTo rdf:type owl:ObjectProperty ;
      rdfs:domain :DateRangeTEI ;
      rdfs:range :Date .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#locatedAt
:locatedAt rdf:type owl:ObjectProperty ;
           rdfs:domain :GeographicalPossession ;
           rdfs:range :Location .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#occurredOn
:occurredOn rdf:type owl:ObjectProperty ;
            rdfs:domain :EventFactoid ;
            rdfs:range :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#referencesLocation
:referencesLocation rdf:type owl:ObjectProperty ;
                    rdfs:domain :LocationReference ;
                    rdfs:range :Location .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#referencesPerson
:referencesPerson rdf:type owl:ObjectProperty ;
                  rdfs:domain :PersonReference ;
                  rdfs:range :Person .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#sourcedFrom
:sourcedFrom rdf:type owl:ObjectProperty ;
             rdfs:domain :Assertion ;
             rdfs:range :SourceCitation .


#################################################################
#    Data properties
#################################################################

###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasBibliographicEntry
:hasBibliographicEntry rdf:type owl:DatatypeProperty ,
                                owl:FunctionalProperty ;
                       rdfs:domain :Source ;
                       rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasDay
:hasDay rdf:type owl:DatatypeProperty ,
                 owl:FunctionalProperty ;
        rdfs:domain :Date ;
        rdfs:range [ rdf:type rdfs:Datatype ;
                     owl:onDatatype xsd:integer ;
                     owl:withRestrictions ( [ xsd:maxInclusive 31
                                            ]
                                          )
                   ] .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasDisplayName
:hasDisplayName rdf:type owl:DatatypeProperty ,
                         owl:FunctionalProperty ;
                rdfs:domain :Person ;
                rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasDisplayNameComponent
:hasDisplayNameComponent rdf:type owl:DatatypeProperty ,
                                  owl:FunctionalProperty ;
                         rdfs:domain :Person ;
                         rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasDisplayNumberComponent
:hasDisplayNumberComponent rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty ;
                           rdfs:domain :Person ;
                           rdfs:range xsd:int .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasEventName
:hasEventName rdf:type owl:DatatypeProperty ,
                       owl:FunctionalProperty ;
              rdfs:domain :EventFactoid ;
              rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasISO8601Date
:hasISO8601Date rdf:type owl:DatatypeProperty ,
                         owl:FunctionalProperty ;
                rdfs:domain :Date ;
                rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasLocationName
:hasLocationName rdf:type owl:DatatypeProperty ,
                          owl:FunctionalProperty ;
                 rdfs:domain :Location ;
                 rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasMonth
:hasMonth rdf:type owl:DatatypeProperty ,
                   owl:FunctionalProperty ;
          rdfs:domain :Date ;
          rdfs:range [ rdf:type rdfs:Datatype ;
                       owl:onDatatype xsd:integer ;
                       owl:withRestrictions ( [ xsd:maxInclusive 12
                                              ]
                                            )
                     ] .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasNameInSourceAs
:hasNameInSourceAs rdf:type owl:DatatypeProperty ,
                            owl:FunctionalProperty ;
                   rdfs:domain :Reference ;
                   rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasPlaceInSource
:hasPlaceInSource rdf:type owl:DatatypeProperty ,
                           owl:FunctionalProperty ;
                  rdfs:domain :SourceCitation ;
                  rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasPossessionName
:hasPossessionName rdf:type owl:DatatypeProperty ,
                            owl:FunctionalProperty ;
                   rdfs:domain :Possession ;
                   rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasRoleName
:hasRoleName rdf:type owl:DatatypeProperty ;
             rdfs:domain :Role ;
             rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasSourceID
:hasSourceID rdf:type owl:DatatypeProperty ,
                      owl:FunctionalProperty ;
             rdfs:domain :Source ;
             rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasSourceName
:hasSourceName rdf:type owl:DatatypeProperty ,
                        owl:FunctionalProperty ;
               rdfs:domain :Source ;
               rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasTextualDescription
:hasTextualDescription rdf:type owl:DatatypeProperty ,
                                owl:FunctionalProperty ;
                       rdfs:domain :DateRange ;
                       rdfs:range xsd:string .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#hasYear
:hasYear rdf:type owl:DatatypeProperty ,
                  owl:FunctionalProperty ;
         rdfs:domain :Date ;
         rdfs:range xsd:integer .


#################################################################
#    Classes
#################################################################

###  http://erlangen-crm.org/current/E39_Actor
cidoc:E39_Actor rdf:type owl:Class .


###  http://erlangen-crm.org/current/E53_Place
cidoc:E53_Place rdf:type owl:Class .


###  http://www.ifla.org/files/assets/cataloguing/FRBRoo/frbroo_v_2.4.pdf#F2_Expression
frbroo:F2_Expression rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Assertion
:Assertion rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#CIDOC_Actor
:CIDOC_Actor rdf:type owl:Class ;
             rdfs:subClassOf cidoc:E39_Actor ,
                             :Person .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#CIDOC_Place
:CIDOC_Place rdf:type owl:Class ;
             rdfs:subClassOf cidoc:E53_Place ,
                             :Location .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Date
:Date rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#DateRange
:DateRange rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#DateRangeCompound
:DateRangeCompound rdf:type owl:Class ;
                   rdfs:subClassOf :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#DateRangeTEI
:DateRangeTEI rdf:type owl:Class ;
              rdfs:subClassOf :DateRange .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#EventFactoid
:EventFactoid rdf:type owl:Class ;
              rdfs:subClassOf :Factoid ;
              owl:disjointWith :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#FRBRSource
:FRBRSource rdf:type owl:Class ;
            rdfs:subClassOf frbroo:F2_Expression ,
                            :Source .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Factoid
:Factoid rdf:type owl:Class ;
         rdfs:subClassOf :Assertion .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#FemalePerson
:FemalePerson rdf:type owl:Class ;
              rdfs:subClassOf :Person .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#GeographicalPossession
:GeographicalPossession rdf:type owl:Class ;
                        rdfs:subClassOf :Possession .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Group
:Group rdf:type owl:Class ;
       rdfs:subClassOf :Person .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Institution
:Institution rdf:type owl:Class ;
             rdfs:subClassOf :Group .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Location
:Location rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#LocationReference
:LocationReference rdf:type owl:Class ;
                   rdfs:subClassOf :Reference .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#MalePerson
:MalePerson rdf:type owl:Class ;
            rdfs:subClassOf :Person .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#NongeographicalPossession
:NongeographicalPossession rdf:type owl:Class ;
                           rdfs:subClassOf :Possession .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#OccupationFactoid
:OccupationFactoid rdf:type owl:Class ;
                   rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#OfficeFactoid
:OfficeFactoid rdf:type owl:Class ;
               rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Person
:Person rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#PersonReference
:PersonReference rdf:type owl:Class ;
                 rdfs:subClassOf :Reference .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Possession
:Possession rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#PossessionFactoid
:PossessionFactoid rdf:type owl:Class ;
                   rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Reference
:Reference rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#ReferenceAsObject
:ReferenceAsObject rdf:type owl:Class ;
                   rdfs:subClassOf :PersonReference ;
                   owl:disjointWith :ReferenceAsSubject .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#ReferenceAsSubject
:ReferenceAsSubject rdf:type owl:Class ;
                    rdfs:subClassOf :PersonReference .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#RelationshipFactoid
:RelationshipFactoid rdf:type owl:Class ;
                     rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Role
:Role rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Source
:Source rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#SourceCitation
:SourceCitation rdf:type owl:Class .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#StateOfAffairsFactoid
:StateOfAffairsFactoid rdf:type owl:Class ;
                       rdfs:subClassOf :Factoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#StatusFactoid
:StatusFactoid rdf:type owl:Class ;
               rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#TitleFactoid
:TitleFactoid rdf:type owl:Class ;
              rdfs:subClassOf :StateOfAffairsFactoid .


###  https://github.com/johnBradley501/FPO/raw/master/fpo.owl#Transaction
:Transaction rdf:type owl:Class ;
             rdfs:subClassOf :EventFactoid .


#################################################################
#    General axioms
#################################################################

[ rdf:type owl:AllDisjointClasses ;
  owl:members ( :FemalePerson
                :Group
                :MalePerson
              )
] .


[ rdf:type owl:AllDisjointClasses ;
  owl:members ( :OccupationFactoid
                :OfficeFactoid
                :PossessionFactoid
                :RelationshipFactoid
                :StatusFactoid
                :TitleFactoid
              )
] .


###  Generated by the OWL API (version 4.5.9.2019-02-01T07:24:44Z) https://github.com/owlcs/owlapi


PLEASE EXTRACT ALL FACTOIDS IN THE CORPUS RELATED TO JEAN SAMMET. Jean Sammet is mentioned in every document. 

"""

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def find_context_in_pdf(pdf_path, search_string, threshold=1000):
    text = extract_text_from_pdf(pdf_path)
    matches = []
    for match in re.finditer(re.escape(search_string), text, flags=re.IGNORECASE):
        start = max(0, match.start() - threshold)
        end = min(len(text), match.end() + threshold)
        context = text[start:end]
        matches.append(context)
    return "".join(str(i) for i in matches)

def generate_rdf_from_text(text, model_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": model_prompt},
            {"role": "user", "content": text[:10000]}  # truncate if large
        ],
        temperature=1
    )
    return response["choices"][0]["message"]["content"]

for filename in os.listdir(pdf_dir):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, filename)
        text = find_context_in_pdf(pdf_path,"Sammet")
        rdf_output = generate_rdf_from_text(text, data_model_prompt)

        rdf_file = os.path.join(output_dir, filename.replace(".pdf", ".ttl"))
        with open(rdf_file, "w", encoding="utf-8") as f:
            f.write(rdf_output)

        print(f"Processed: {filename} → {rdf_file}")