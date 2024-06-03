#!/bin/bash

#SBATCH --job-name=orgs
#SBATCH --account=juliame0
#SBATCH --partition=standard
#SBATCH --time=08-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --mail-type=BEGIN,END,FAIL



srun python get_organization_accounts.py