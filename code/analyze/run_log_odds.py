import os
import sys
import glob
from itertools import combinations
import pathlib
from multiprocessing import Pool



frame_list = ['diagnostic','prognostic','motivational','identify','blame','solution','tactics','solidarity','counter']


# linguistic_features = ['hashtags','mentions','tokens', 'lemmas','verb_lemmas', 'noun_lemmas', 
#                        'adjective_lemmas', 'pronouns', 'verb_tense', 
#                        'pronoun_number', 'pronoun_person', 'subject_verb', 'verb_object', 'noun_chunks']

linguistic_features = ['hashtags','mentions','tokens', 'lemmas','verb_lemmas', 'noun_lemmas', 
                       'adjective_lemmas', 'subject_verb', 'verb_object', 'noun_chunks']

subgroups_list = [[],['movement'],['protest_activity'],['stance'],['stakeholder_group'],
                 ['movement','protest_activity'],['movement','stance'],['movement','stakeholder_group'],
                 ['protest_activity','stakeholder_group']]

movements = ['lgbtq','immigration','guns']



base_dir = "/nfs/turbo/si-juliame/social-movements/feature_counts_08-16-2023"
log_odds_dir ="/nfs/turbo/si-juliame/social-movements/log_odds_08-18-2023"
pathlib.Path(log_odds_dir).mkdir(parents=True,exist_ok=True)


programs = []
#for movement in movements:
for feature in linguistic_features:
    for frame in frame_list:
        file1 = os.path.join(base_dir,feature,frame,'stakeholder_group',f'journalist.json')
        file2 = os.path.join(base_dir,feature,frame,'stakeholder_group',f'smo.json')
        filep = os.path.join(base_dir,feature,frame,'full.json')
        #filep = os.path.join(base_dir,feature,'all_frames','full.json')
        out_dir = os.path.join(log_odds_dir,f'stakeholder_group_journalist_vs_smo')
        pathlib.Path(out_dir).mkdir(parents=True,exist_ok=True)
        out_file = os.path.join(out_dir,f"{feature}_{frame}.tsv")
        program =f"python log_odds.py -f {file1} -s {file2} -p {filep} --out_file {out_file} --min_count=0"
        programs.append(program)
        #os.system(program)

with Pool(36) as p:
    p.map(os.system,programs)


