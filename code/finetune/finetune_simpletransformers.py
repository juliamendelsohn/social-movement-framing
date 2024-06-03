from simpletransformers.language_modeling import  LanguageModelingModel
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

trainfile='/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/train.raw'
evalfile='/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/dev.raw'
outdir='/nfs/turbo/si-juliame/social-movements/ft_roberta_simpletransformers/'

model_args = {
        'num_train_epochs':5,
        "use_early_stopping": True,
        "output_dir": outdir,
        "overwrite_output_dir": True,
        "manual_seed": 42,
        "save_eval_checkpoints": False,
        "save_steps": -1,
        "train_batch_size": 128,
        "n_gpu": 2,
}

model = LanguageModelingModel("roberta", "roberta-base",args=model_args,use_cuda=cuda_available)
model.train_model(trainfile)
