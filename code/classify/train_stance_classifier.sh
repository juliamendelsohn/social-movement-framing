#!/bin/bash
#SBATCH --job-name=stance
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=00-3:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --mail-type=BEGIN,END,FAIL


categories="Task2:stance"
epochs=20
seed=42
batchsize=32
# modelpath='roberta-base'
# modelname='roberta-base'
modelpath='/nfs/turbo/si-juliame/social-movements/ft_roberta_simpletransformers'
modelname='roberta-ft-st'

date="06-21-2023"
datadir="/home/juliame/social-movements/annotated_data/data_splits_${date}"
baseoutdir="/nfs/turbo/si-juliame/social-movements/roberta_models/${modelname}/stance_${date}"


trainfile="${datadir}/train_relevant.tsv"
outdir="${baseoutdir}/all_movements/"
categories=${categories}
mkdir -p ${outdir}
python train_roberta.py \
    --train-file=${trainfile} \
    --output-dir=${outdir} \
    --categories=${categories} \
    --num-epochs=${epochs} \
    --manual-seed=${seed} \
    --train-batch-size=${batchsize} \
    --model-path=${modelpath}


for fold in 0 1 2 3 4;
    do
    trainfile="${datadir}/fold_${fold}/train_relevant.tsv"
    outdir="${baseoutdir}/fold_${fold}/all_movements/"
    categories=${categories}
    mkdir -p ${outdir}
    python train_roberta.py \
    --train-file=${trainfile} \
    --output-dir=${outdir} \
    --categories=${categories} \
    --num-epochs=${epochs} \
    --manual-seed=${seed} \
    --train-batch-size=${batchsize} \
    --model-path=${modelpath}
    done


for fold in 0 1 2 3 4;
    do
    for movement in guns immigration lgbtq;
        do
        trainfile="${datadir}/fold_${fold}/train_relevant_${movement}.tsv"
        outdir="${baseoutdir}/fold_${fold}/${movement}/"
        categories=${categories}
        mkdir -p ${outdir}
        python train_roberta.py \
        --train-file=${trainfile} \
        --output-dir=${outdir} \
        --categories=${categories} \
        --num-epochs=${epochs} \
        --manual-seed=${seed} \
        --train-batch-size=${batchsize} \
        --model-path=${modelpath}
    done
done



for movement in guns immigration lgbtq;
    do
    trainfile="${datadir}/train_relevant_${movement}.tsv"
    outdir="${baseoutdir}/${movement}/"
    categories=${categories}
    mkdir -p ${outdir}
    python train_roberta.py \
    --train-file=${trainfile} \
    --output-dir=${outdir} \
    --categories=${categories} \
    --num-epochs=${epochs} \
    --manual-seed=${seed} \
    --train-batch-size=${batchsize} \
    --model-path=${modelpath}
done
