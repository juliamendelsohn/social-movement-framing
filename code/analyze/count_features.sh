#!/bin/bash
#SBATCH --job-name=lingfeature
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=00-12:00:00
#SBATCH --mem=128gb
#SBATCH --mail-type=BEGIN,END,FAIL

python count_features.py