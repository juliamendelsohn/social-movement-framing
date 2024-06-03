#!/bin/bash

#SBATCH --job-name=predict
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=01-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --mail-type=BEGIN,END,FAIL



# for trainsetting in guns immigration lgbtq leave_out_guns leave_out_immigration leave_out_lgbtq;
#     do
#     modeldir="/nfs/turbo/si-juliame/social-movements/roberta_models/04-12-2023/movement_splits/${trainsetting}/"
#     for evalsetting in guns immigration lgbtq;
#         do
#         evalfile="/home/juliame/social-movements/annotated_data/movement_splits/04-12-2023/${evalsetting}.tsv"
#         outfile="/home/juliame/social-movements/annotated_data/roberta_preds/04-12-2023/movement_splits/${trainsetting}_train_${evalsetting}_eval.tsv"
#         python predict_roberta.py \
#         --eval-file=${evalfile} \
#         --model-dir=${modeldir} \
#         --out-file=${outfile}
#     done
# done




trainsetting="augmented_train"

modeldir="/nfs/turbo/si-juliame/social-movements/roberta_models/04-12-2023/data_frac_splits/${trainsetting}/"
evalfile="/home/juliame/social-movements/annotated_data/data_frac_splits/04-12-2023_0.8train_0dev_0.2test/test.tsv"
outfile="/home/juliame/social-movements/annotated_data/roberta_preds/04-12-2023/data_frac_splits/${trainsetting}.tsv"
mkdir -p ${outdir}
python predict_roberta.py \
--eval-file=${evalfile} \
--model-dir=${modeldir} \
--out-file=${outfile}

        


# for issue in all_issues lgbtq immigration guns;
#     do
#     for model in all_issues lgbtq immigration guns;
#         do
#             eval_dataset=majority_agreement_50
#             train_dataset=${eval_dataset}
#             base_data_dir=/home/juliame/social-movements/stance_data
#             base_model_dir=/nfs/turbo/si-juliame/social-movements/stance_roberta_models
#             base_eval_dir=/nfs/turbo/si-juliame/social-movements/stance_roberta_eval
#             evalfile="${base_data_dir}/${eval_dataset}/${issue}_dev.tsv"
#             modeldir="${base_model_dir}/${train_dataset}/${model}/"
#             outfile="${base_eval_dir}/${eval_dataset}/${issue}_trained_on_${model}_${train_dataset}_data.tsv"
#             srun python predict_roberta.py \
#             --eval-issue=${issue} \
#             --eval-file=${evalfile} \
#             --model-dir=${modeldir} \
#             --out-file=${outfile} &
#         done
#     done


# for filter in 0 33 50 67;
#     do 
#     for issue in all_issues lgbtq immigration guns;
#         do
#         for model in all_issues lgbtq immigration guns;
#             do
#                 eval_dataset=majority_agreement_50
#                 train_dataset=individual_labels_worker_filter_${filter}
#                 base_data_dir=/home/juliame/social-movements/stance_data
#                 base_model_dir=/nfs/turbo/si-juliame/social-movements/stance_roberta_models
#                 base_eval_dir=/nfs/turbo/si-juliame/social-movements/stance_roberta_eval
#                 evalfile="${base_data_dir}/${eval_dataset}/${issue}_dev.tsv"
#                 modeldir="${base_model_dir}/${train_dataset}/${model}/"
#                 outfile="${base_eval_dir}/${eval_dataset}/${issue}_trained_on_${model}_${train_dataset}_data.tsv"
#                 srun python predict_roberta.py \
#                 --eval-issue=${issue} \
#                 --eval-file=${evalfile} \
#                 --model-dir=${modeldir} \
#                 --out-file=${outfile} &
#             done
#         done
#     done 

# wait

