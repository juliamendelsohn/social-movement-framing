#!/bin/bash

#SBATCH --job-name=predict-relevance
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=00-03:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --mail-type=BEGIN,END,FAIL


categories="Task1:relevance"
#modelname='roberta-base'
modelname='roberta-ft-st'
#modelname='roberta-ft'
date="06-21-2023"
datadir="/home/juliame/social-movements/annotated_data/data_splits_${date}"
modelbase="/nfs/turbo/si-juliame/social-movements/roberta_models/${modelname}/relevance_${date}"
outdir="/home/juliame/social-movements/predictions/${modelname}/relevance_${date}"


modeldir="${modelbase}/all_movements/"
evalfile="${datadir}/test_full.tsv"
outfile="${outdir}/test_full.tsv"
categories=${categories}
mkdir -p ${outdir}
python predict_roberta.py \
    --eval-file=${evalfile} \
    --model-dir=${modeldir} \
    --categories=${categories} \
    --out-file=${outfile} 



for fold in 0 1 2 3 4;
    do
    modeldir="${modelbase}/fold_${fold}/all_movements/"
    evalfile="${datadir}/fold_${fold}/dev_full.tsv"
    outfile="${outdir}/fold_${fold}/dev_full.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python predict_roberta.py \
        --eval-file=${evalfile} \
        --model-dir=${modeldir} \
        --categories=${categories} \
        --out-file=${outfile} 
    done


for fold in 0 1 2 3 4;
    do
    for movement in guns immigration lgbtq;
        do
        modeldir="${modelbase}/fold_${fold}/${movement}/"
        evalfile="${datadir}/fold_${fold}/dev_full_${movement}.tsv"
        outfile="${outdir}/fold_${fold}/dev_full_${movement}.tsv"
        categories=${categories}
        mkdir -p ${outdir}
        python predict_roberta.py \
            --eval-file=${evalfile} \
            --model-dir=${modeldir} \
            --categories=${categories} \
            --out-file=${outfile} 
        done
    done



for movement in guns immigration lgbtq;
    do
    modeldir="${modelbase}/${movement}/"
    evalfile="${datadir}/test_full_${movement}.tsv"
    outfile="${outdir}/test_full_${movement}.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python predict_roberta.py \
        --eval-file=${evalfile} \
        --model-dir=${modeldir} \
        --categories=${categories} \
        --out-file=${outfile} 
    done
