
import os

import spacy
from collections import Counter

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
            file_path = os.path.join("data", "Damballa_Report_IMDDOS.pdf")
            print(file_path)

            #clean(file_path, 2)

            cleaned_file_path = file_path.split('.')  # in case the file has many . in the name
            cleaned_file_path[-2] = cleaned_file_path[-2] + "_parsed-sections"
            cleaned_file_path[-1] = 'txt'
            cleaned_file_path = '.'.join(cleaned_file_path)
            print("Opening", cleaned_file_path)
            with open(cleaned_file_path, 'r') as f:
                cleaned_text = f.read()
                
                ### Run NER on the cleaned text, get most commonly mentioned named entities ###
                
                nlp = spacy.load("en_core_web_sm")
                # Need to run command in terminal:
                #   python -m spacy download en_core_web_sm
                
                doc = nlp(cleaned_text)
                # for ent in doc.ents[:10]:
                #     print(ent.text, ent.label_)
                
                # ents = [(x.text, x.label_) for x in doc.ents]
                # print(*Counter(ents).most_common()[:20], sep='\n')

                print("Named entities as recognized by Spacy NER model, with most commonly mentioned at top")
                ents = [x.text for x in doc.ents if not x.text.isnumeric() and x.label_ is not "DATE"]

                most_common = Counter(ents).most_common()[:20]
                #print(*most_common[:20], sep='\n')
                
                for idx, ent in enumerate(most_common):
                    print('{:<5} {}({})'.format(str(idx+1)+'.', ent[0], ent[1]), sep='\n')
                
            break


if __name__ == '__main__':
    main()
