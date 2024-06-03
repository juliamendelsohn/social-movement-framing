#!/bin/bash
#SBATCH --job-name=topicmodel
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=00-08:00:00
#SBATCH --mem=16gb
#SBATCH --mail-type=BEGIN,END,FAIL

python train_topic_model.py