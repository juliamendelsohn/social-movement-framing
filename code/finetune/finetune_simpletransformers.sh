#!/bin/bash

#SBATCH --job-name=finetune-lm
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=2
#SBATCH --time=10-00:00:00
#SBATCH --mem=10gb
#SBATCH --mail-type=BEGIN,END,FAIL

python finetune_simpletransformers.py