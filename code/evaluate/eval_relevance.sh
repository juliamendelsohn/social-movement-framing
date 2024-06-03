#!/bin/bash

categories='Task1:relevance'
shortname="relevance"
#modelname='roberta-base'
#modelname='roberta-ft'
modelname='roberta-ft-st'

date="06-21-2023"
predbase="/home/juliame/social-movements/predictions/${modelname}/${shortname}_${date}"
outbase="/home/juliame/social-movements/evaluations/${modelname}/${shortname}_${date}"



predfile="${predbase}/test_full.tsv"
outdir="${outbase}"
outfilename="test_full.tsv"
categories=${categories}
mkdir -p ${outdir}
python eval_roberta.py \
 --predict-file=${predfile} \
 --out-dir=${outdir} \
 --out-filename=${outfilename} \
 --categories=${categories}


for fold in 0 1 2 3 4;
    do
    predfile="${predbase}/fold_${fold}/dev_full.tsv"
    outdir="${outbase}/fold_${fold}"
    outfilename="dev_full.tsv"
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
        predfile="${predbase}/fold_${fold}/dev_full_${movement}.tsv"
        outdir="${outbase}/fold_${fold}"
        outfilename="dev_full_${movement}.tsv"
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
    predfile="${predbase}/test_full_${movement}.tsv"
    outdir="${outbase}"
    outfilename="test_full_${movement}.tsv"
    categories=${categories}
    mkdir -p ${outdir}
    python eval_roberta.py \
    --predict-file=${predfile} \
    --out-dir=${outdir} \
    --out-filename=${outfilename} \
    --categories=${categories}
    done




