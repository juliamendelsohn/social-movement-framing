#!/bin/bash

# categories="Task1:relevance"
# shortname="relevance"
# split='full'

# categories="Task2:stance"
# shortname='stance'
# split='relevant'

# categories="Task3:diagnostic,Task4:prognostic,Task5:motivational"
# shortname="macro-frames"
# split='relevant'

categories="Task3:identify,Task3:blame,Task4:solution,Task4:tactics,Task4:solidarity,Task4:counter,Task5:motivational"
shortname="frame-elements"
split='relevant'

modelmovement='all_movements'
modelname='roberta-ft-st'
date="06-21-2023"
predbase="/home/juliame/social-movements/predictions/${modelname}/${modelmovement}_model_preds/${shortname}_${date}"
outbase="/home/juliame/social-movements/evaluations/${modelname}/${modelmovement}_model_eval/${shortname}_${date}"

for fold in 0 1 2 3 4;
    do
    for movement in guns immigration lgbtq;
        do
        predfile="${predbase}/fold_${fold}/dev_${split}_${movement}.tsv"
        outdir="${outbase}/fold_${fold}"
        outfilename="dev_${split}_${movement}.tsv"
        categories=${categories}
        mkdir -p ${outdir}
        python eval_roberta.py \
        --predict-file=${predfile} \
        --out-dir=${outdir} \
        --out-filename=${outfilename} \
        --categories=${categories}
        done
    done

for movement in guns immigration lgbtq;
    do
    predfile="${predbase}/test_${split}_${movement}.tsv"
    outdir="${outbase}"
    outfilename="test_${split}_${movement}.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python eval_roberta.py \
    --predict-file=${predfile} \
    --out-dir=${outdir} \
    --out-filename=${outfilename} \
    --categories=${categories}
    done