# -*- coding: utf-8 -*-

import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from datetime import datetime
import sys
import uuid
import json
default_spacy_tagger = en_core_web_sm.load()
custom_spacy_tagger = spacy.load('damballa_train')

def stuff_that_happens(FILE):
    
    # STIX Bundle to hold SDOs
    sdo_bundle = {"type": 'bundle',
              "id": 'bundle--'+str(uuid.uuid5(uuid.NAMESPACE_DNS,FILE)),
              "spec_version": "2.0",
              "objects": []
              }
    
    # List to hold all created STIX Domain Objects (SDOs)
    sdo_list = []
    
    # Initial creation SDO for the report itself.
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
    #default_entities = [(entity.text, entity.label_) for entity in default_parsing.ents]
    custom_entities = [(entity.text, entity.label_) for entity in custom_parsing.ents]
    
    
    # Entity identification frequencies throughout the document if needed
    #default_entity_frequency = Counter(default_entities)
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
        creation_sdo["name"] = most_common[custom_entity_index][0][0]
        creation_sdo["description"] = ''
        creation_sdo["labels"] = []
        sdo_list.append(creation_sdo)
        
        custom_entity_index += 1


    # Potential place for Bradley's section
    
    



    

     # User interaction loop that allows creation of custom sdos
    print()
    user_interaction_complete = False
    first_prompt = True
    while not user_interaction_complete:
        if first_prompt:
            print('\nInput "help" for command help')
            first_prompt = False
            
        user_input = input("Please input a command: ")
        
        # Help command
        if user_input == 'help':
            print('Available commands are: create malware ;<malware name> ;<malware description>')
            print('                      : create threat-actor <threat-actor name> <threat-actor description>')
            print('                      : sdo_list (prints the currently created sdos)')
            print('                      : sdo_drop <sdo index> (drops the sdo from the sdo list)')
            print('                      : sdo_edit ;<sdo index>; <sdo key>; <new value> (edits the key-value pair of the sdo at index)')
            print('                      : save (saves the current sdo_list into a .json file)')
            print('                      : complete (exits the user interaction loop and stops the program)')
        
        # Create custom malware/threat-actor sdos
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
            sdo_list.append(temp_sdo)
            
        # Print out all the currently created sdos
        if user_input == 'sdo_list':
            sdo_index = 0
            for item in sdo_list:
                print(f'[{sdo_index}] {item}\n')
                sdo_index += 1
                
        # Drop one of the currently created sdos
        if user_input[0:8] == 'sdo_drop':
            tokenised_input = user_input.split()
            if not len(tokenised_input) == 2:
                print('Please only input one index argument')
            else:
                del sdo_list[int(tokenised_input[1])]
                print(f'Deleted sdo with index {tokenised_input[1]}')
                
        # Edit a key-value pair of the indexed sdo (need to limit it to type, name, description, labels)
        if user_input[0:8] == 'sdo_edit':
            tokenised_input = user_input.split(';')
            if not len(tokenised_input) == 4:
                print('Please follow the following 3 argument format: sdo_edit ;<sdo index>; <sdo key>; <new value>')
            else:
                if not int(tokenised_input[1]) < len(sdo_list):
                    print("INDEX OUT OF BOUNDS. RETRY")
                elif not tokenised_input[2] in sdo_list[int(tokenised_input[1])]:
                    print("Please enter a valid sdo key")
                else:
                    sdo_list[int(tokenised_input[1])][tokenised_input[2]] = tokenised_input[3]
                    print(f"Value of {tokenised_input[2]} key in sdo [{tokenised_input[1]}] is now {tokenised_input[3]}")
                    sdo_list[int(tokenised_input[1])]["modified"] = str(datetime.now())
        
        # Save sdo-list to a file
        if user_input == 'save':
            filename = input("Gimme a file name: ")
            for sdo in sdo_list:
                if not sdo["type"] == 'report':
                    sdo_list[0]["object_refs"].append(sdo["id"])
            sdo_bundle["objects"] = sdo_list
            jsonDump = json.dumps(sdo_bundle)
            save_file = open(filename, 'w')
            save_file.write(jsonDump)
            save_file.close()
            print(f"Bundle saved to {filename}")
        
        # End user interaction loop
        if user_input == 'complete':
            print('Exiting the user input loop')
            user_interaction_complete = True
            
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: python running_test.py -r <textfile>")
        exit()
    FILE = sys.argv[2]
    stuff_that_happens(FILE)
