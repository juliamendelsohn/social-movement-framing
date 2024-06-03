from simpletransformers.classification import  MultiLabelClassificationModel, MultiLabelClassificationArgs,ClassificationModel
from transformers import AutoTokenizer
import os
from ast import literal_eval
import pandas as pd
import sklearn
import torch
import argparse
import logging
import csv 

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)
cuda_available = torch.cuda.is_available()


def contains_prognostic(s):
    if 'Task4:solution' in s and s['Task4:solution']==1:
        return 1
    elif 'Task4:tactics' in s and s['Task4:tactics']==1:
        return 1
    elif 'Task4:solidarity' in s and  s['Task4:solidarity']==1:
        return 1
    elif 'Task4:counter' in s and s['Task4:counter']==1:
        return 1
    return 0



def load_data(train_file,categories):
    df = pd.read_csv(train_file,sep='\t',quoting=csv.QUOTE_NONE)
    df['Task4:prognostic'] = df.apply(contains_prognostic,axis=1)

    if len(categories) > 1:
        df['labels'] = df[categories].values.tolist()
    else:
        df['labels'] = df[categories[0]]
    print(df)
    print(df[['text','labels']])
    return df[['text','labels']]




def configure_model_args(args):
    output_dir = args.output_dir
    num_epochs = args.num_epochs
    manual_seed = args.manual_seed
    train_batch_size = args.train_batch_size

    model_args = {
        'num_train_epochs':num_epochs,
        'fp16': True,
        "use_early_stopping": True,
        "output_dir": output_dir,
        "overwrite_output_dir": True,
        "manual_seed": manual_seed,
        "save_eval_checkpoints": False,
        "save_steps": -1,
        "train_batch_size": train_batch_size,
        "save_model_every_epoch": False,
    }
    return model_args


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file",help='full path to training data file')
    parser.add_argument("--output-dir",help = 'output directory')
    parser.add_argument("--num-epochs",type=int,help='number of epochs to train')
    parser.add_argument("--manual-seed",type=int,help='seed for replicability')
    parser.add_argument("--train-batch-size",type=int,help='batch size for training')
    parser.add_argument("--categories",type=str,help='list of categories to train on, comma separated')
    parser.add_argument("--model-path",type=str,help='path to model to load')




    args = parser.parse_args()
    train_file = args.train_file
    categories = args.categories.split(',')
    model_path = args.model_path
    print(categories)

    train_df = load_data(train_file,categories)    
    model_args = configure_model_args(args)
    print("trainfile:",train_file)
    print("categories:",categories)
    print("model args:",model_args)
    print("outdir:",args.output_dir)
    print(train_df)



    if len(categories) == 1:
        num_labels = train_df['labels'].nunique()
        model = ClassificationModel('roberta',model_path,
            args=model_args,
            use_cuda=cuda_available,
            num_labels=num_labels,
        )
        model.train_model(train_df)

    else:
        num_labels = len(train_df['labels'][0])
        model = MultiLabelClassificationModel('roberta',model_path, 
            num_labels=num_labels,
            args=model_args,
            use_cuda=cuda_available,
        ) 
        model.train_model(train_df)




if __name__ == "__main__":
	main()
