import os
import pathlib
import re
import json
from collections import Counter, defaultdict
import pandas as pd
import argparse



def word_count_list_of_strings(list_of_strings):
    word_counts = Counter()
    for string in list_of_strings:
        word_counts.update(string.split())
    return word_counts

def get_wc_per_label(df):
    label_to_wc = defaultdict(Counter)
    for label in df['label'].unique():
        label_to_wc[label] = word_count_list_of_strings(df[df['label'] == label]['words'].tolist())
    return label_to_wc

def write_word_counts(word_counts_per_label,out_dir):
    pathlib.Path(out_dir).mkdir(parents=True,exist_ok=True)
    for label,word_counts in word_counts_per_label.items():
        l = label.split('/')[0]
        with open(os.path.join(out_dir,f"{l}.json"),'w') as f:
            json.dump(word_counts,f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file",help = 'input_file')
    parser.add_argument("--out-dir",help = 'word counts directory')
    args = parser.parse_args()

    df = pd.read_csv(args.input_file,sep='\t')
    df['words'] =  df['text'].apply(lambda x:re.sub(r'[^#a-zA-Z0-9 ]+', '', x).strip().lower())

    word_counts_per_label = get_wc_per_label(df)
    word_counts_per_label['full'] = word_count_list_of_strings(df['words'].tolist())
    write_word_counts(word_counts_per_label,args.out_dir)



if __name__ == '__main__':
    main()

