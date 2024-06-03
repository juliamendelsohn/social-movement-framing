#!/bin/bash

#modelname='roberta-base'
modelname='roberta-ft-st'
date="06-21-2023"
# predbase="/home/juliame/social-movements/predictions/roberta_binary_models/${modelname}"
# outbase="/home/juliame/social-movements/evaluations/roberta_binary_models/${modelname}"

predbase="/home/juliame/social-movements/predictions/roberta_augmented_models/${modelname}/train_with_1k_per_movement_generations"
outbase="/home/juliame/social-movements/evaluations/roberta_augmented_models/${modelname}/train_with_1k_per_movement_generations"



categories="Task4:solution Task4:tactics Task4:solidarity Task4:counter Task5:motivational"
for category in ${categories};
    do
    IFS=: read -r task shortname <<< ${category}

    preddir="${predbase}/${shortname}"
    predfile="${preddir}/test_relevant.tsv"
    outdir="${outbase}/${shortname}"
    outfilename="test_relevant.tsv"

    mkdir -p ${outdir}
    python eval_roberta.py \
    --predict-file=${predfile} \
    --out-dir=${outdir} \
    --out-filename=${outfilename} \
    --categories=${category}

    for fold in 0 1 2 3 4;
        do
        preddir="${predbase}/${shortname}/fold_${fold}"
        predfile="${preddir}/dev_relevant.tsv"
        outdir="${outbase}/${shortname}/fold_${fold}"
        outfilename="dev_relevant.tsv"

        mkdir -p ${outdir}
        python eval_roberta.py \
        --predict-file=${predfile} \
        --out-dir=${outdir} \
        --out-filename=${outfilename} \
        --categories=${category}
        done
    done
