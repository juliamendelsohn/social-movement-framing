#!/bin/bash
#SBATCH --job-name=lingfeature
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=00-12:00:00
#SBATCH --mem=64gb
#SBATCH --mail-type=BEGIN,END,FAIL

python get_linguistic_features.py