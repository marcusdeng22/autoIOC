
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

            full_text = clean(file_path, 2)
            
            for section in full_text:
                for idx, sentence in enumerate(section):
                    if sentence.startswith("Figure"):
                        del section[idx]
            # For some reason gets some, but not all???

            for section in full_text:
                for sentence in section:
                    print(sentence, end='\n\n')
            print('-----------------------------------')

            # cleaned_file_path = file_path.split('.')  # in case the file has many . in the name
            # cleaned_file_path[-2] = cleaned_file_path[-2] + "_parsed-sections"
            # cleaned_file_path[-1] = 'txt'
            # cleaned_file_path = '.'.join(cleaned_file_path)
            # print("Opening", cleaned_file_path)
            # with open(cleaned_file_path, 'r') as f:
            #     cleaned_text = f.read()#.lower()
                
            #     ### Run NER on the cleaned text, get most commonly mentioned named entities ###
                
            #     nlp = spacy.load("en_core_web_sm")
            #     # Need to run command in terminal:
            #     #   python -m spacy download en_core_web_sm
                
            #     doc = nlp(cleaned_text)
            #     # for ent in doc.ents[:10]:
            #     #     print(ent.text, ent.label_)
                
            #     # ents = [(x.text, x.label_) for x in doc.ents]
            #     # print(*Counter(ents).most_common()[:20], sep='\n')

            #     print("Named entities as recognized by Spacy NER model, with most commonly mentioned at top")
            #     ents = [x.text for x in doc.ents if not x.text.isnumeric() and x.label_ is not "DATE"]

            #     most_common = Counter(ents).most_common()[:20]
            #     #print(*most_common[:20], sep='\n')
                
            #     for idx, ent in enumerate(most_common):
            #         print('{:<5} {}({})'.format(str(idx+1)+'.', ent[0], ent[1]), sep='\n')
                
            #     #selections = [1, 3]
            #     selection = 3#int(input("Select entity to summarize: "))
            #     selection = most_common[selection-1][0]
            #     print(selection)



            #     ### Look for selected entity in each section
            #     sections = cleaned_text.split('++++++++++++++++')[:-2]
            #         # Excluding summary, plus a random thing at the end.
            #     counts = []
            #     for section in sections:
            #         count = 0
            #         for word in section.split(' '):
            #             if word == selection:
            #                 count += 1
            #         counts.append(count)
            #     print(counts, "sum:", sum(counts))

            #     # So, turns out that not every instance of an entity in the text is
            #     # recognized as an entity. Is this good or bad?
                
            #     # Also, some sections have Figure "sentences" that are meant to describe
            #     # some figure, say a chart or graph. These contribute to the count of
            #     # entities in the section even if the section doesn't actually describe
            #     # the entity very well.

            #     # text summarization over each sentence containing the entity.
            #     nlp = English()
            #     nlp.add_pipe(nlp.create_pipe('sentencizer')) # updated
            #     doc = nlp(cleaned_text)
            #     sentences = [sent.string.strip() for sent in doc.sents]
            #     #print(*sentences[:30], sep='\n\n')

            #     containing_sentences = []
            #     for sentence in sentences:
            #         doc = nlp(sentence)
            #         entities = [x.label for x in doc.ents]
            #         if selection in entities:
            #             # could just look for the work, but trying to recognize it
            #             # as an entity again.
                        





            break


if __name__ == '__main__':
    main()
