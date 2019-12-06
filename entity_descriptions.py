
import os
from collections import Counter

import spacy
from spacy.lang.en import English

from textcleaner import clean
from text_summarizer import generate_summary

# We can use Spacy NER to get named entities
# We can separate the document into sections based on the table of contents

# Goal:
#   Scan entire document, get most commonly mentioned named entities.
#   For each entity,
#       count how many times it was mentioned in each section.
#       Run text summarization on the section with the highest number of counts for the entity, making sure to pick sentences that include (namely, that describe) the entity.


def get_descriptions(cleaned_text, chosen_entity):
    
    for file in os.listdir("data"):
        if file.endswith(".pdf"):
            file_path = os.path.join("data", file)
            file_path = os.path.join("data", "Damballa_Report_IMDDOS.pdf")
            print(file_path)


            # ### Look for selected entity in each section
            # counts = []
            # for section in cleaned_text:
            #     count = 0
            #     for chunk in section[1:]:
            #         for word in chunk.split(' '):
            #             if word == selection:
            #                 count += 1
            #     counts.append(count)
            # print(counts, "sum:", sum(counts))
            # # Not good to split on spaces, since an entity may consist of multiple words

            # # So, turns out that not every instance of an entity in the text is
            # # recognized as an entity. Is this good or bad?


            # Break cleaned_text into individual sentences
            # Select sentences that contain the entity we are looking for.
            nlp = English()
            nlp.add_pipe(nlp.create_pipe('sentencizer')) # updated
            containing_sentences = []
            sentences = []
            for section in cleaned_text:
                count = 0
                for chunk in section[1:]:
                    doc = nlp(chunk)
                    chunk_sentences = [sent.string.strip() for sent in doc.sents]
                    sentences.extend(chunk_sentences)
                    for sentence in chunk_sentences:
                        if chosen_entity in sentence:
                            containing_sentences.append(sentence)

            
            # ## NEVERMIND, literally missed IMDDOS in a sentence. Harrumph.
            # nlp = spacy.load("en_core_web_sm")
            # containing_sentences = []
            # for sentence in sentences:
            #     doc = nlp(sentence)
            #     entities = [x.text for x in doc.ents]
            #     print("Sentence:", sentence)
            #     print("Entities:", entities)
            #     print()
            #     if selection in entities:
            #         # could just look for the word, but trying to recognize it
            #         # as an entity again.
            #         containing_sentences.append(sentence)

            # print("Containing sentences:")
            # for sentence in containing_sentences:
            #     print(sentence, end='\n\n')
            
            summary_sentences = generate_summary(containing_sentences)
            return summary_sentences


if __name__ == '__main__':
    main()
