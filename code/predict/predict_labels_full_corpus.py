from simpletransformers.classification import MultiLabelClassificationModel, ClassificationModel, ClassificationArgs
import os
from ast import literal_eval
import pandas as pd
import torch
import argparse
import numpy as np
import logging
import pathlib
import csv
from multiprocessing import Pool 
import psutil


logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)
cuda_available = torch.cuda.is_available()


def load_data(data_file):
    df = pd.read_csv(data_file,sep='\t',quoting=csv.QUOTE_NONE,dtype=str)
    return df[['tweet_id','text']]


def build_model(model_dir,categories,num_labels,batch_size,num_processes):
    model_args = ClassificationArgs()
    model_args.eval_batch_size = batch_size
    model_args.dataloader_num_workers = num_processes
    print(model_args)
    print('cuda_available',cuda_available)

    if len(categories) == 1:
        model = ClassificationModel('roberta',model_dir, 
            use_cuda=cuda_available,
            num_labels=num_labels,
            args=model_args,
        )
    else:
        model = MultiLabelClassificationModel('roberta',model_dir, 
            num_labels=num_labels,
            use_cuda=cuda_available,
            args=model_args,
        )
    return model 
    

def predict(model,df_subset,out_file):
    preds, model_outputs = model.predict(df_subset['text'].tolist())
    df_subset['preds'] = preds
    df_subset.to_csv(out_file,sep='\t')
     

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-file",help='full path to data file')
    parser.add_argument("--model-dir",help = 'model directory')
    parser.add_argument("--out-dir",help = 'predictions dir')
    parser.add_argument("--categories",type=str,help='list of categories to train on, comma separated')
    parser.add_argument("--num-labels",type=int,help='number of labels')
    parser.add_argument("--batch-size",type=int,help='batch size')
    parser.add_argument("--num-processes",type=int,help="number of processes to use")

    args = parser.parse_args()
    print(args)


    data_file = args.data_file
    categories = args.categories.split(',')
    num_labels = args.num_labels
    model_dir = args.model_dir
    batch_size = args.batch_size
    num_processes = args.num_processes
    model = build_model(model_dir,categories,num_labels,batch_size,num_processes)

    df = load_data(data_file)  
    df_subsets = np.array_split(df,200)

    out_dir = args.out_dir
    pathlib.Path(out_dir).mkdir(parents=True,exist_ok=True)
    out_files = [os.path.join(out_dir,f'preds_{i}.tsv') for i in range(len(df_subsets))]

    num_cpus = psutil.cpu_count(logical=True)
    print('Number of available CPUs:', num_cpus)

    # func_tuples = [(model,df_subset,out_file) for df_subset,out_file in zip(df_subsets,out_files)]
    # pool = Pool(num_processes)
    # pool.starmap(predict,func_tuples)

    # Single version
    for df_subset,out_file in zip(df_subsets,out_files):
        print('Predicting on',out_file)
        predict(model,df_subset,out_file)







  




if __name__ == "__main__":
	main()