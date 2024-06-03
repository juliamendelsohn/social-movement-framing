import pandas as pd
import spacy
from collections import Counter
import re
import json
import os

print(os.cpu_count())

nlp = spacy.load("en_core_web_sm")
process_count = 4



def load_corpus(corpus_file):
    df = pd.read_csv(corpus_file, sep='\t',dtype={'tweet_id': str})
    text_col = 'text_x'
    texts = df[text_col].tolist()
    # remove all hashtags in texts (we have hashtags stored in the metadata)
    texts = [text.replace('#','') for text in texts]
    # identify all links that start with http and remove them
    texts = [re.sub(r'http\S+', '', text) for text in texts]
    # replace all occurrences of &amp with and
    texts = [text.replace('&amp;','and') for text in texts]
    docs = nlp.pipe(texts,n_process=process_count,batch_size=1000)
    tweet_ids = df['tweet_id'].tolist()
    return docs,tweet_ids

def get_noun_chunks(doc):
    noun_chunks = []
    for chunk in doc.noun_chunks:
        # make sure that the chunk isn't all usernames
        if all([token.text.startswith('@') for token in chunk]):
            continue
        # make sure that the chunk isn't all hashtags
        if all([token.text.startswith('#') for token in chunk]):
            continue
        # if first word is determiner, exclude it from chunk
        if chunk[0].pos_ == 'DET':
            noun_chunks.append(chunk[1:].text.lower())
        else:
            noun_chunks.append(chunk.text.lower())
    return Counter(noun_chunks)



def get_token_level_counts(doc):
    counts = {}
    counts['tokens'] = Counter()
    counts['lemmas'] = Counter()
    counts['verbs'] = Counter()
    counts['verb_lemmas'] = Counter()
    counts['nouns'] = Counter()
    counts['noun_lemmas'] = Counter()
    counts['adjectives'] = Counter()
    counts['adjective_lemmas'] = Counter()
    counts['pronouns'] = Counter()

    for token in doc:
        pos = token.pos_
        if pos in ['PUNCT','SPACE','SYM','NUM','X'] or token.like_url or token.like_num:
            continue
        counts['tokens'][token.text.lower()] += 1
        counts['lemmas'][token.lemma_.lower()] += 1
        if pos in ['VERB','AUX']:
            counts['verbs'][token.text.lower()] += 1
            counts['verb_lemmas'][token.lemma_.lower()] += 1
        elif pos in ['NOUN','PROPN']:
            counts['nouns'][token.text.lower()] += 1
            counts['noun_lemmas'][token.lemma_.lower()] += 1
        elif pos in ['ADJ']:
            counts['adjectives'][token.lemma_.lower()] += 1
            counts['adjective_lemmas'][token.lemma_.lower()] += 1
        elif pos in ['PRON']:
            counts['pronouns'][token.text.lower()] += 1
    return counts
        

def get_morphological_features(doc):
    counts = {}
    counts['verb_tense'] = Counter()
    counts['pronoun_number'] = Counter()
    counts['pronoun_person'] = Counter()
    
    for token in doc:
        pos = token.pos_
        if pos in ['VERB','AUX']:
            tense = token.morph.get('Tense')
            if len(token.morph.get('Tense')) > 0:
                counts['verb_tense'][tense[0]] += 1
        elif pos in ['PRON']:
            number = token.morph.get('Number')
            person = token.morph.get('Person')
            if len(number) > 0:
                counts['pronoun_number'][number[0]] += 1
            if len(person) > 0:
                counts['pronoun_person'][person[0]] += 1
    return counts


def get_dependency_features(doc):
    counts = {}
    counts['subject_verb'] = Counter()
    counts['verb_object'] = Counter()

    for chunk in doc.noun_chunks:
        noun = chunk.root
        head = noun.head
        if noun.dep_ == 'nsubj' and head.pos_ == 'VERB':
            counts['subject_verb'][noun.lemma_.lower() + '_' + head.lemma_.lower()] += 1
        elif noun.dep_ == 'dobj' and head.pos_ == 'VERB':
            counts['verb_object'][head.lemma_.lower() + '_' + noun.lemma_.lower()] += 1
        elif noun.dep_ == 'pobj' and head.dep_ == 'agent' and head.head.pos_ == 'VERB':
            counts['subject_verb'][noun.lemma_.lower() + '_' + head.head.lemma_.lower()] += 1
        elif noun.dep_ == 'nsubjpass' and head.pos_ == 'VERB':
            counts['verb_object'][head.lemma_.lower() + '_' + noun.lemma_.lower()] += 1
    return counts

def get_entities(doc):
    counts = {}
    counts['entity_person'] = Counter()
    counts['entity_org'] = Counter()
    counts['entity_norp'] = Counter()
    counts['entity_gpe'] = Counter()
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            counts['entity_person'][ent.text.lower()] += 1
        elif ent.label_ == 'ORG':
            counts['entity_org'][ent.text.lower()] += 1
        elif ent.label_ == 'NORP':
            counts['entity_norp'][ent.text.lower()] += 1
        elif ent.label_ == 'GPE':
            counts['entity_gpe'][ent.text.lower()] += 1
    return counts
        


def main():
    corpus_file = '/nfs/turbo/si-juliame/social-movements/full_corpus_with_preds_and_stakeholders_08-02-2023.tsv'
    out_file = '/nfs/turbo/si-juliame/social-movements/ling_features_sm_full_corpus_with_preds_and_stakeholders_08-16-2023.jsonl'
    docs,tweet_ids = load_corpus(corpus_file)

    with open(out_file,'w') as f:
        for doc,tweet_id in zip(docs,tweet_ids):
            all_feature_counts = {}
            all_feature_counts['tweet_id'] = tweet_id
            all_feature_counts.update(get_token_level_counts(doc))
            all_feature_counts.update(get_morphological_features(doc))
            all_feature_counts.update(get_dependency_features(doc))
            all_feature_counts.update(get_entities(doc))
            all_feature_counts['noun_chunks'] = get_noun_chunks(doc)
            f.write(json.dumps(all_feature_counts) + '\n')
    

    

    

if __name__ == '__main__':
    main()