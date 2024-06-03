#!/bin/bash

categories='Task2:stance'
shortname="stance"
#modelname='roberta-base'
modelname='roberta-ft-st'
date="06-21-2023"
predbase="/home/juliame/social-movements/predictions/${modelname}/${shortname}_${date}"
outbase="/home/juliame/social-movements/evaluations/${modelname}/${shortname}_${date}"


predfile="${predbase}/test_relevant.tsv"
outdir="${outbase}"
outfilename="test_relevant.tsv"
categories=${categories}
mkdir -p ${outdir}
python eval_roberta.py \
 --predict-file=${predfile} \
 --out-dir=${outdir} \
 --out-filename=${outfilename} \
 --categories=${categories}


for fold in 0 1 2 3 4;
    do
    predfile="${predbase}/fold_${fold}/dev_relevant.tsv"
    outdir="${outbase}/fold_${fold}"
    outfilename="dev_relevant.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python eval_roberta.py \
    --predict-file=${predfile} \
    --out-dir=${outdir} \
    --out-filename=${outfilename} \
    --categories=${categories}
    done


for fold in 0 1 2 3 4;
    do
    for movement in guns immigration lgbtq;
        do
        predfile="${predbase}/fold_${fold}/dev_relevant_${movement}.tsv"
        outdir="${outbase}/fold_${fold}"
        outfilename="dev_relevant_${movement}.tsv"
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
    predfile="${predbase}/test_relevant_${movement}.tsv"
    outdir="${outbase}"
    outfilename="test_relevant_${movement}.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python eval_roberta.py \
    --predict-file=${predfile} \
    --out-dir=${outdir} \
    --out-filename=${outfilename} \
    --categories=${categories}
    done




