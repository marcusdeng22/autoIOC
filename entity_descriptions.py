
import os
import subprocess

from textcleaner import clean

# We can use Spacy NER to get named entities
# We can separate the document into sections based on the table of contents

# Goal:
#   Scan entire document, get most commonly mentioned named entities.
#   For each entity,
#       count how many times it was mentioned in each section.
#       Run text summarization on the section with the highest number of counts for the entity, making sure to pick sentences that include (namely, that describe) the entity.


def main():
    
    for file in os.listdir("data"):
        if file.endswith(".pdf"):
            file_path = os.path.join("data", file)
            print(file)

            #clean(file_path, 2)

            cleaned_file_path = file_path.split('.')  # in case the file has many . in the name
            cleaned_file_path[-2] = cleaned_file_path[-2] + "_parsed-sections"
            cleaned_file_path[-1] = 'txt'
            cleaned_file_path = '.'.join(cleaned_file_path)
            print("Opening", cleaned_file_path)
            #with open(cleaned_file_path, 'r') as f:
                

            #break


if __name__ == '__main__':
    main()
