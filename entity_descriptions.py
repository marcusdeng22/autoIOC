
import os
from collections import Counter

import spacy
from spacy.lang.en import English

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

            cleaned_text = clean(file_path, 2)
            
            # Get rid of sentences that start with "Figure"
            for section in cleaned_text:
                for idx, sentence in enumerate(section):
                    if sentence.startswith("Figure"):
                        del section[idx]
            # For some reason gets some, but not all???

            # Get rid of summary section, because it has a bunch of random crap after it
            del cleaned_text[-1]

            # for section in full_text:
            #     for sentence in section:
            #         print(sentence, end='\n\n')
            # print('-----------------------------------')

            # cleaned_file_path = file_path.split('.')  # in case the file has many . in the name
            # cleaned_file_path[-2] = cleaned_file_path[-2] + "_parsed-sections"
            # cleaned_file_path[-1] = 'txt'
            # cleaned_file_path = '.'.join(cleaned_file_path)
            # print("Opening", cleaned_file_path)
            # with open(cleaned_file_path, 'r') as f:
            #     cleaned_text = f.read()#.lower()
                
            ### Run NER on the cleaned text, get most commonly mentioned named entities ###
            
            nlp = spacy.load("en_core_web_sm")
            # Need to run command in terminal:
            #   python -m spacy download en_core_web_sm
            
            block_of_text = ''
            for section in cleaned_text:
                #print(section, end='\n\n\n')
                block_of_text += ' '.join(section[1:])  # Ignoring section header
            #print(block_of_text)

            doc = nlp(block_of_text)
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
            
            #selections = [1, 3]
            selection = 3#int(input("Select entity to summarize: "))
            selection = most_common[selection-1][0]
            print(selection)


            ### Look for selected entity in each section
            counts = []
            for section in cleaned_text:
                count = 0
                for chunk in section[1:]:
                    for word in chunk.split(' '):
                        if word == selection:
                            count += 1
                counts.append(count)
            print(counts, "sum:", sum(counts))

            # So, turns out that not every instance of an entity in the text is
            # recognized as an entity. Is this good or bad?


            # Break cleaned_text into individual sentences
            nlp = English()
            nlp.add_pipe(nlp.create_pipe('sentencizer')) # updated
            sentences = []
            for section in cleaned_text:
                count = 0
                for chunk in section[1:]:
                    doc = nlp(chunk)
                    chunk_sentences = [sent.string.strip() for sent in doc.sents]
                    # for sentence in chunk_sentences:
                    #     print(sentence)
                    #     print()
                    sentences.extend(chunk_sentences)
            
            for sentence in sentences:
                print(sentence, end='\n\n')





            # containing_sentences = []
            # for sentence in sentences:
            #     doc = nlp(sentence)
            #     entities = [x.label for x in doc.ents]
            #     if selection in entities:
            #         # could just look for the work, but trying to recognize it
            #         # as an entity again.
            #         pass

            break


if __name__ == '__main__':
    main()
