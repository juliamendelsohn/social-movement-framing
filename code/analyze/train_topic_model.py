import os
from pathlib import Path
from multiprocessing import Pool
import sys
import time
import little_mallet_wrapper as lmw


base_data_dir = '/nfs/turbo/si-juliame/social-movements/topic_model_data_08-19-2023/'
base_out_dir = '/nfs/turbo/si-juliame/social-movements/topic_model_output_08-20-2023/'
Path(base_out_dir).mkdir(parents=True, exist_ok=True)
path_to_mallet = '/nfs/turbo/si-juliame/Mallet/bin/mallet'


def train_model(dataset):
    in_dir = os.path.join(base_data_dir,dataset)
    out_dir = os.path.join(base_out_dir,dataset)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    num_topics = 50
    with open(os.path.join(in_dir,'tokens.txt')) as f:
        training_data = [lmw.process_string(x.strip(),numbers='keep') for x in f.readlines()]
    keys, dists = lmw.quick_train_topic_model(path_to_mallet,out_dir,num_topics,training_data)
    

def main():
    datasets = os.listdir(base_data_dir)
    with Pool(17) as p:
        p.map(train_model,datasets)
    

if __name__ == "__main__":
    main()

