#!/bin/bash
#SBATCH --job-name=prepregression
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=00-12:00:00
#SBATCH --mem=128gb
#SBATCH --mail-type=BEGIN,END,FAIL

python prep_features_for_regression.py