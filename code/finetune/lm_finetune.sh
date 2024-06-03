#!/bin/bash

#SBATCH --job-name=finetune-lm
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=2
#SBATCH --time=10-00:00:00
#SBATCH --mem=10gb
#SBATCH --mail-type=BEGIN,END,FAIL



trainfile='/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/train.raw'
evalfile='/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/dev.raw'
outdir='/nfs/turbo/si-juliame/social-movements/finetune_roberta_mlm_all_issues/'
#modelname='roberta-base'
modelname='/nfs/turbo/si-juliame/social-movements/finetune_roberta_mlm_all_issues/checkpoint-2038223'
epochs=1

python mlm_finetune.py \
--train_data_file=${trainfile} \
--eval_data_file=${evalfile} \
--output_dir=${outdir} \
--model_type=${modelname} \
--num_train_epochs=${epochs} 




# trainfile="/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/train.raw"
# testfile="/nfs/turbo/si-juliame/social-movements/finetune_data/all_issues/dev.raw"
# outdir="/nfs/turbo/si-juliame/social-movements/roberta_finetune_all_issues/"
# srun python run_language_modeling.py \
# --output_dir=${outdir} \
# --model_type=roberta \
# --model_name_or_path=/nfs/turbo/si-juliame/social-movements/roberta_finetune_all_issues/checkpoint-4593000/ \
# --do_train \
# --train_data_file=${trainfile} \
# --do_eval \
# --eval_data_file=${testfile} \
# --mlm \
# --line_by_line \
# --num_train_epochs=10 \
# --save_steps=50000 \
# --save_total_limit=10 #\
# # --block_size=64 \
# # --per_gpu_train_batch_size=64   \
# #--model_name_or_path=roberta-base \





