#!/bin/bash
#SBATCH --job-name=pred-relevance
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=07-00:00:00
#SBATCH --mem=32gb
#SBATCH --mail-type=BEGIN,END,FAIL


categories="Task1:relevance"
shortname="relevance"
split='full'
numlabels=2

# categories="Task2:stance"
# shortname='stance'
# split='relevant'
# numlabels=3

# categories="Task3:diagnostic,Task4:prognostic,Task5:motivational"
# shortname="macro-frames"
# split='relevant'
# numlabels=3

# categories="Task3:identify,Task3:blame,Task4:solution,Task4:tactics,Task4:solidarity,Task4:counter,Task5:motivational"
# shortname="frame-elements"
# split='relevant'
# numlabels=7

datafile="/nfs/turbo/si-juliame/social-movements/full_corpus_08-02-2023.tsv"

date="06-21-2023"
modelname='roberta-ft-st'
modelbase="/nfs/turbo/si-juliame/social-movements/roberta_models/${modelname}/${shortname}_${date}"
modeldir="${modelbase}/all_movements/"

outdir="/nfs/turbo/si-juliame/social-movements/full_predictions/${modelname}/${shortname}_${date}"

categories=${categories}
mkdir -p ${outdir}
python predict_labels_full_corpus.py \
    --data-file=${datafile} \
    --model-dir=${modeldir} \
    --categories=${categories} \
    --out-dir=${outdir} \
    --num-labels=${numlabels} \
    --batch-size=64 \
    --num-processes=8