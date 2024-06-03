import simpledorff
# from nltk.metrics.agreement import AnnotationTask
# from nltk.metrics import masi_distance,jaccard_distance
import pandas as pd 
import numpy as np 
import os
import simpledorff
from itertools import combinations

#coder, item, annotation

# All annotations are located here 'social-movements/annotations/{date}/{coder}.tsv'
def load_annotation_file(annotation_path,annotation_chunk_date,coders):
    dfs = []
    for coder in coders:
        annotation_file = os.path.join(annotation_path,annotation_chunk_date,coder+'.tsv')
        df = pd.read_csv(annotation_file,sep='\t')
        df.columns = df.columns.str.replace('\t','')
        df.columns = df.columns.str.replace(' ','')
        df['coder'] = coder
        print(df.columns)
        dfs.append(df)
    df = pd.concat(dfs,sort=True)
    #remove unnamed column from dataframe
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    #remove any whitespace (tabs and spaces) in column names
    df.columns = df.columns.str.replace('\t','')
    df.columns = df.columns.str.replace(' ','')
    return df
    


#stance separations
def create_additional_stance_labels(df):
    df['Task2:stance-pro'] = [1 if x=='pro' else 0 for x in df['Task2:stance']]
    df['Task2:stance-anti'] = [1 if x=='anti' else 0 for x in df['Task2:stance']]
    pro_explicit_list = []
    anti_explicit_list = []
    for i,row in df.iterrows():
        if row['Task2:stance-explicit'] == 'yes' and row['Task2:stance'] == 'pro':
            pro_explicit_list.append(1)
        else:
            pro_explicit_list.append(0)
        if row['Task2:stance-explicit'] == 'yes' and row['Task2:stance'] == 'anti':
            anti_explicit_list.append(1)
        else:
            anti_explicit_list.append(0)
    df['Task2:stance-pro-explicit'] = pro_explicit_list
    df['Task2:stance-anti-explicit'] = anti_explicit_list
    return df
 

def create_frame_category_columns(df):
    diagnostic_list = []
    prognostic_list = []
    for i,row in df.iterrows():
        if 'yes' in list(row[df.columns.str.contains('Task3')]):
            diagnostic_list.append('yes')
        else:
            diagnostic_list.append('no')
        if 'yes' in list(row[df.columns.str.contains('Task4')]):
            prognostic_list.append('yes')
        else:
            prognostic_list.append('no')
    df['Task3:all-diagnostic'] = diagnostic_list
    df['Task4:all-prognostic'] = prognostic_list
    return df



def calculate_agreement(df,task,coders='all',movement='all'):
    df_sub = df.copy()
    if coders != 'all':
        df_sub = df_sub[df_sub['coder'].isin(coders)]
    if movement != 'all':
        df_sub = df_sub[df_sub['movement']==movement]
    res = {}
    res['coders'] = coders
    res['movement'] = movement
    res['task'] = task
    try:
        res['alpha'] = simpledorff.calculate_krippendorffs_alpha_for_df(df_sub,experiment_col='id_str',
                                                 annotator_col='coder',
                                                 class_col=task)
    except:
        res['alpha'] = None
    return res


#final datasheet should have:
# coders (including "all"), movement (including "all"),task, score
def calculate_all_agreement(df):
    tasks = [c for c in sorted(df.columns) if c.startswith('Task')]
    results = []


    movements = list(set(df['movement'])) + ['all']
    coders = list(set(df['coder']))
    coder_pairs = list(combinations(coders,2)) + ['all']

    for movement in movements:
        for coder_pair in coder_pairs:
            for task in tasks:
                res = calculate_agreement(df,task,coders=coder_pair,movement=movement)
                results.append(res)
    return pd.DataFrame(results)
        

def get_disagreement_cells(df_grouped):
    df_consensus = df_grouped.copy()
    for col in df_consensus.columns:
        if type(df_consensus[col][0]) == list:
            new_col = []
            for row in range(len(df_consensus)):
                if len(set(df_consensus[col][row]))==1:
                    new_col.append(df_consensus[col][row][0])
                else:
                    new_col.append('TODO')
            df_consensus[col] = new_col
    return df_consensus

def get_number_disagreements(df_consensus):
    num_rows = 0
    num_cells = 0
    for i,row in df_consensus.iterrows():
        row_todos = len([x for x in list(row) if x=='TODO'])
        num_cells += row_todos
        if row_todos >=1:
            num_rows += 1
    print(num_rows,num_cells)



def write_consensus_file(annotation_path,annotation_chunk_date,coders,out_dir):
    coders_str = '_'.join(coders)
    df = load_annotation_file(annotation_path,annotation_chunk_date,coders)
    df_grouped = df.groupby(by=['id_str','text','movement']).agg(list).reset_index()
    df_grouped = df_grouped.drop(columns='coder')
    df_consensus = get_disagreement_cells(df_grouped)
    get_number_disagreements(df_consensus)
    df_original_order = df.drop_duplicates(subset=['id_str','text','movement'])[['id_str','text','movement']]
    df_consensus = df_original_order.merge(df_consensus,on=['id_str','text','movement'],how='left')
    df_consensus.to_csv(os.path.join(out_dir,f'pre_meeting_consensus_{annotation_chunk_date}_{coders_str}.tsv'),sep='\t',index=False) 

def subset_to_agreed_relevant(df):
    df_grouped = df.groupby(by=['id_str','text','movement']).agg(list).reset_index()
    relevance_ids = df_grouped[df_grouped['Task1:relevance'].apply(lambda x: len(set(x))==1)]['id_str'].to_list()
    df_relevance = df[df['id_str'].isin(relevance_ids) & (df['Task1:relevance']=='yes')]
    return df_relevance

def main():
    annotation_path = '/home/juliame/social-movements/annotated_data/'
    # annotation_chunk_date = '02-13-2023'
    eval_dir = '/home/juliame/social-movements/annotated_data/eval/'
    # eval_chunk_dir = os.path.join(eval_dir,annotation_chunk_date)
    # if not os.path.exists(eval_dir):
    #     os.mkdir(eval_dir)
    # if not os.path.exists(eval_chunk_dir):
    #     os.mkdir(eval_chunk_dir)

    coders = ['Julia','Maya','Consensus','ChatGPT']
    #write_consensus_file(annotation_path,annotation_chunk_date,coders,eval_chunk_dir)

    # df = load_annotation_file(annotation_path,annotation_chunk_date,coders)
    # print(df)
    # df = create_additional_stance_labels(df)
    # df = create_frame_category_columns(df)

    # results = calculate_all_agreement(df)
    # results.to_csv(os.path.join(eval_chunk_dir,f'agreement_scores_{annotation_chunk_date}.tsv'),sep='\t',index=False)

    # df_rel = subset_to_agreed_relevant(df)
    # results_rel = calculate_all_agreement(df_rel)
    # results_rel.to_csv(os.path.join(eval_chunk_dir,f'agreement_scores_{annotation_chunk_date}_relevant_only.tsv'),sep='\t',index=False)

    dfs = []
    for annotation_chunk_date in ['02-13-2023','03-13-2023','03-21-2023']:
        new_df = load_annotation_file(annotation_path,annotation_chunk_date,coders)
        if 'Notes' in new_df.columns:
            new_df = new_df.drop(columns=['Notes'])
        dfs.append(new_df)
    df = pd.concat(dfs)
    print(df)

    df = create_frame_category_columns(df)
    # replace incorrect values that are not yes or no with no
    for col in df.columns:
        if col.startswith('Task') and col != 'Task2:stance':
            df[col] = df[col].apply(lambda x: 'no' if x not in ['yes','no'] else x)
        elif col.startswith('Task2:'):
            df[col] = df[col].apply(lambda x: 'neutral/unclear' if x not in ['pro','anti','neutral/unclear'] else x)
    
    print(df)

    results = calculate_all_agreement(df)
    results.to_csv(os.path.join(eval_dir,f'agreement_with_chatgpt_03-29-2023.tsv'),sep='\t',index=False)

    df_rel = subset_to_agreed_relevant(df)
    results_rel = calculate_all_agreement(df_rel)
    results_rel.to_csv(os.path.join(eval_dir,f'agreement_with_chatgpt_03-29-2023_relevant_only.tsv'),sep='\t',index=False)


   



if __name__ == '__main__':
    main()



