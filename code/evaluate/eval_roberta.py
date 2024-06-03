from sklearn.metrics import f1_score, classification_report
import pandas as pd
import os
from collections import defaultdict
import pathlib
import argparse
import scipy
import numpy as np
from ast import literal_eval


categories = ['Task1:relevance',
'Task2:stance-pro',
'Task2:stance-neutral',
'Task2:stance-anti',
'Task2:stance-explicit',
'Task3:identify',
'Task3:blame',
'Task4:solution',
'Task4:tactics',
'Task4:solidarity',
'Task4:counter',
'Task5:motivational']


def load_eval_data(filename,categories):
    df = pd.read_csv(filename,sep='\t')
    if len(categories) > 1:
        df['labels'] = df['labels'].apply(lambda x: literal_eval(x))
        df['preds'] = df['preds'].apply(lambda x: literal_eval(x))

        y_true = list(df['labels'])
        y_pred = list(df['preds'])

        y_true = np.matrix(y_true)
        y_pred = np.matrix(y_pred)

        return y_true,y_pred
    else:
        y_true = df['labels']
        y_pred = df['preds']
    return y_true,y_pred
    


def calculate_eval_metrics(y_true,y_pred,out_dir,out_filename,categories):

    #If multiple categories:
    if len(categories) > 1:
        report = pd.DataFrame(classification_report(y_true,y_pred,
        target_names=categories,output_dict=True,zero_division=0)).transpose()
    else:
        report = pd.DataFrame(classification_report(y_true,y_pred,
        output_dict=True,zero_division=0)).transpose()
    report.to_csv(os.path.join(out_dir,out_filename),sep='\t',index=True)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predict-file",help = 'predictions file')
    parser.add_argument("--out-dir",help = 'evaluation results directory')
    parser.add_argument("--out-filename",help = 'evaluation results filename')
    parser.add_argument("--categories",type=str,help='list of categories to train on, comma separated')

    
    args = parser.parse_args()
    categories = args.categories.split(',')
    predict_file = args.predict_file
    out_dir = args.out_dir
    filename = args.out_filename
    pathlib.Path(out_dir).mkdir(parents=True,exist_ok=True)
    y_true,y_pred = load_eval_data(predict_file,categories)
    calculate_eval_metrics(y_true,y_pred,out_dir,filename,categories)


   



if __name__ == "__main__":
    main()