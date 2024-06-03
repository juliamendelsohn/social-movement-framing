from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import pandas as pd
import os
from collections import defaultdict
import pathlib

def load_eval_data(filename):
    df = pd.read_csv(filename,sep='\t')
    y_true = df['labels'].tolist()
    y_pred = df['preds'].tolist()
    return y_true,y_pred
    

def calculate_eval_metrics(y_true, y_pred):
    """Calculates evaluation metrics for a given set of true and predicted labels.

    Args:
        y_true (list): List of true labels.
        y_pred (list): List of predicted labels.

    Returns:
        dict: Dictionary of evaluation metrics.
    """
    f1_per_class = f1_score(y_true, y_pred, average=None)
    f1_pro,f1_neutral,f1_anti = f1_per_class[0],f1_per_class[1],f1_per_class[2]
    return {
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_micro": f1_score(y_true, y_pred, average="micro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "f1_pro": f1_pro,
        "f1_neutral": f1_neutral,
        "f1_anti": f1_anti,
    }



def main():
    eval_data_dir = '/nfs/turbo/si-juliame/social-movements/stance_roberta_eval/majority_agreement_50'
    metric_dir = '/nfs/turbo/si-juliame/social-movements/eval_metric_summary/'
    pathlib.Path(metric_dir).mkdir(parents=True,exist_ok=True)
    issues = ['lgbtq','guns','immigration','all_issues']
    all_eval_metrics = []

    for data_issue in issues:
        for model_issue in issues:
            base_filename = f"{data_issue}_issue_trained_on_{model_issue}.tsv"
            filename = os.path.join(eval_data_dir,base_filename)
            y_true,y_pred = load_eval_data(filename)
            
            eval_metrics = calculate_eval_metrics(y_true, y_pred)
            eval_metrics['data_issue'] = data_issue
            eval_metrics['model_issue'] = model_issue

            all_eval_metrics.append(eval_metrics)

    eval_metric_summary = pd.DataFrame(all_eval_metrics)
    eval_metric_summary.to_csv(os.path.join(metric_dir,'majority_agreement_50.tsv'),sep='\t',index=False)
            



if __name__ == "__main__":
    main()