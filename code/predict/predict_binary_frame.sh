#!/bin/bash
#SBATCH --job-name=frame-elements
#SBATCH --account=juliame0
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=00-03:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem=5gb
#SBATCH --mail-type=BEGIN,END,FAIL

date="06-21-2023"
modelname='roberta-ft-st'
evalbase="/home/juliame/social-movements/annotated_data/data_splits_${date}"
# modelbase="/nfs/turbo/si-juliame/social-movements/roberta_binary_models/${modelname}"
# outbase="/home/juliame/social-movements/predictions/roberta_binary_models/${modelname}"
modelbase="/nfs/turbo/si-juliame/social-movements/roberta_augmented_models/${modelname}/train_with_1k_per_movement_generations"
outbase="/home/juliame/social-movements/predictions/roberta_augmented_models/${modelname}/train_with_1k_per_movement_generations"



categories="Task3:identify Task3:blame Task4:solution Task4:tactics Task4:solidarity Task4:counter Task5:motivational"
for category in ${categories};
    do
    IFS=: read -r task shortname <<< ${category}
    modeldir="${modelbase}/${shortname}/all_movements/"
    evalfile="${evalbase}/test_relevant.tsv"
    outdir="${outbase}/${shortname}"
    outfile="${outdir}/test_relevant.tsv"
    mkdir -p ${outdir}
    python predict_roberta.py \
        --eval-file=${evalfile} \
        --model-dir=${modeldir} \
        --categories=${category} \
        --out-file=${outfile} 

    for fold in 0 1 2 3 4;
        do
        modeldir="${modelbase}/${shortname}/fold_${fold}/all_movements/"
        evalfile="${evalbase}/fold_${fold}/dev_relevant.tsv"
        outdir="${outbase}/${shortname}/fold_${fold}"
        outfile="${outdir}/dev_relevant.tsv"
        mkdir -p ${outdir}
        python predict_roberta.py \
            --eval-file=${evalfile} \
            --model-dir=${modeldir} \
            --categories=${category} \
            --out-file=${outfile} 
        done
    done


