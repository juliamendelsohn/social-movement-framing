#!/bin/bash

#SBATCH --job-name=predict
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=00-03:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --mail-type=BEGIN,END,FAIL

categories="Task2:stance"
#modelname='roberta-base'
#modelname='roberta-ft'
modelname='roberta-ft-st'

date="06-21-2023"
evalbase="/home/juliame/social-movements/annotated_data/data_splits_${date}"
modelbase="/nfs/turbo/si-juliame/social-movements/roberta_models/${modelname}/stance_${date}"
outbase="/home/juliame/social-movements/predictions/${modelname}/stance_${date}"




modeldir="${modelbase}/all_movements/"
evalfile="${evalbase}/test_relevant.tsv"
outfile="${outbase}/test_relevant.tsv"
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
    evalfile="${evalbase}/fold_${fold}/dev_relevant.tsv"
    outfile="${outbase}/fold_${fold}/dev_relevant.tsv"
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
        evalfile="${evalbase}/fold_${fold}/dev_relevant_${movement}.tsv"
        outfile="${outbase}/fold_${fold}/dev_relevant_${movement}.tsv"
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
    evalfile="${evalbase}/test_relevant_${movement}.tsv"
    outfile="${outbase}/test_relevant_${movement}.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python predict_roberta.py \
        --eval-file=${evalfile} \
        --model-dir=${modeldir} \
        --categories=${categories} \
        --out-file=${outfile} 
    done
