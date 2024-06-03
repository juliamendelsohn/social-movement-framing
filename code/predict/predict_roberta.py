from simpletransformers.classification import MultiLabelClassificationModel, ClassificationModel
import os
from ast import literal_eval
import pandas as pd
import torch
import argparse
import logging
import pathlib
import csv

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)
cuda_available = torch.cuda.is_available()



def contains_prognostic(s):
    if s['Task4:solution']==1:
        return 1
    elif s['Task4:tactics']==1:
        return 1
    elif s['Task4:solidarity']==1:
        return 1
    elif s['Task4:counter']==1:
        return 1
    return 0

def load_data(eval_file,categories):
    df = pd.read_csv(eval_file,sep='\t',quoting=csv.QUOTE_NONE)
    df['Task4:prognostic'] = df.apply(contains_prognostic,axis=1)
    print(df['Task4:prognostic'].value_counts())

    if len(categories) > 1:
        df['labels'] = df[categories].values.tolist()
    else:
        df['labels'] = df[categories[0]]
    print(df)
    print(df[['text','labels']])
    return df[['text','labels']]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--eval-file",help='full path to eval data file')
    parser.add_argument("--model-dir",help = 'model directory')
    parser.add_argument("--out-file",help = 'evaluation results file')
    parser.add_argument("--categories",type=str,help='list of categories to train on, comma separated')

    args = parser.parse_args()
    eval_file = args.eval_file
    categories = args.categories.split(',')
    print(categories)
    eval_df = load_data(eval_file,categories)    

    model_dir = args.model_dir
    out_file = args.out_file
    pathlib.Path(os.path.dirname(out_file)).mkdir(parents=True,exist_ok=True)


    if len(categories) == 1:
        num_labels = eval_df['labels'].nunique()
        model = ClassificationModel('roberta',model_dir, 
            use_cuda=cuda_available,
            num_labels=num_labels,
        )

    else:
        num_labels = len(eval_df['labels'][0])
        model = MultiLabelClassificationModel('roberta',model_dir, 
            num_labels=num_labels,
            use_cuda=cuda_available,
        ) 


    preds,model_outputs = model.predict(eval_df['text'].tolist())
    result_df = eval_df.copy()
    result_df['preds'] = preds


    model_name = pathlib.PurePath(model_dir).name
    result_df.to_csv(out_file,sep='\t')

  




if __name__ == "__main__":
	main()