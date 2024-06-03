#!/bin/bash
#SBATCH --job-name=prepmallet
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=00-3:00:00
#SBATCH --mem=128gb
#SBATCH --mail-type=BEGIN,END,FAIL

python prepare_tweets_for_mallet.py