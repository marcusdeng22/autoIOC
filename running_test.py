# -*- coding: utf-8 -*-

import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from datetime import datetime
import sys
import uuid
default_spacy_tagger = en_core_web_sm.load()
custom_spacy_tagger = spacy.load('damballa_train')

def stuff_that_happens(FILE):
    
    # List to hold all created sdo
    sdo_list = []
    
    # Initial creation of the report_sdo
    # Figure out how to fill in the description and published categories
    report_sdo = {"type": 'report', 
                  "id": 'report--'+str(uuid.uuid5(uuid.NAMESPACE_DNS, FILE[0:-4])),
                  "created": str(datetime.now()), 
                  "modified": str(datetime.now()), 
                  "name": FILE[0:-4], 
                  "labels":["threat report"],
                  "description": '',
                  "object_refs": [],
                  }
    sdo_list.append(report_sdo)
    
    # Open and read the cleaned text file of the desired pdf report
    with open(FILE, 'r') as report_reader:
        report_contents = report_reader.read()
    
    # Run the report contents through spacy's nlp process using the default and custom models
    default_parsing = default_spacy_tagger(report_contents)
    custom_parsing = custom_spacy_tagger(report_contents)
    
    # Create lists containing the entities and corresponding labels identified by each model
    default_entities = [(entity.text, entity.label_) for entity in default_parsing.ents]
    custom_entities = [(entity.text, entity.label_) for entity in custom_parsing.ents]
    
    # Entity identification frequencies throughout the document if needed
    default_entity_frequency = Counter(default_entities)
    custom_entity_frequency = Counter(custom_entities)
    
    # Printing out the identified entities and their tags
    #print('Entities and their identified frequencies as determined by the default language model')
    #for entity in default_entity_frequency:
    #    print(f'{entity}: {default_entity_frequency[entity]}')
    
    print('\nEntities and their identified frequencies as determined by the custom language model')
    custom_entity_index = 0
    most_common = custom_entity_frequency.most_common()
    for entity in custom_entity_frequency:
        print(f'[{custom_entity_index}] {most_common[custom_entity_index][0]}: {most_common[custom_entity_index][1]}')
        
        # Create sdos for each identified entity determined by the custom language model
        creation_sdo = {}
        creation_sdo["type"] = most_common[custom_entity_index][0][1].lower()
        creation_sdo["id"] = creation_sdo["type"]+str(uuid.uuid5(uuid.NAMESPACE_DNS,most_common[custom_entity_index][0][0]))
        creation_sdo["created"] = str(datetime.now())
        creation_sdo["modified"] = str(datetime.now())
        creation_sdo["description"] = ''
        creation_sdo["labels"] = ''
        sdo_list.append(creation_sdo)
        
        custom_entity_index += 1

        



    # User interaction loop that allows creation of custom sdos
    print()
    user_interaction_complete = False
    first_prompt = True
    while not user_interaction_complete:
        if first_prompt:
            print('\nInput "help" for command help')
            first_prompt = False
            
        user_input = input("Please input a command: ")
        
        if user_input == 'help':
            print('Available commands are: create malware ;<malware name> ;<malware description>')
            print('                      : create threat-actor <threat-actor name> <threat-actor description>')
            print('                      : complete (exits the user interaction loop and stops the program)')
            print('                      : sdo_list (prints the currently created sdos)')
            print('                      : sdo_drop <sdo index> (drops the sdo from the sdo list)')
        if user_input[0:6] == 'create':
            temp_sdo = {}
            tokenised_input = user_input.split(';')
            if user_input[7:14] == 'malware':
                temp_sdo["type"] = "malware"
            if user_input[7:19] == 'threat-actor':
                temp_sdo["type"] = 'threat-actor'
            temp_sdo["id"] = 'malware--'+str(uuid.uuid5(uuid.NAMESPACE_DNS, tokenised_input[1]))
            temp_sdo["created"] = str(datetime.now())
            temp_sdo["modified"] = str(datetime.now())
            temp_sdo["name"] = tokenised_input[1]
            temp_sdo["description"] = tokenised_input[2]
            temp_sdo["labels"] = []
            report_sdo["object_refs"].append(temp_sdo["id"])
            sdo_list.append(temp_sdo)
        if user_input == 'sdo_list':
            sdo_index = 0
            for item in sdo_list:
                print(f'[{sdo_index}] {item}\n')
                sdo_index += 1
        if user_input[0:8] == 'sdo_drop':
            tokenised_input = user_input.split()
            if not len(tokenised_input) == 2:
                print('Please only input one index argument')
            else:
                del sdo_list[int(tokenised_input[1])]
                print(f'Deleted sdo with index {tokenised_input[1]}')
        if user_input == 'complete':
            print('Exiting the user input loop')
            print(report_sdo)
            user_interaction_complete = True

    print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: python running_test.py -r <textfile>")
        exit()
    FILE = sys.argv[2]
    stuff_that_happens(FILE)
