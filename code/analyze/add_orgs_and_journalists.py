import pandas as pd
import os
import csv 
import glob


org_name_map = {
    'npr': 'NPR',
    'nyt': 'NYTimes',
    'breitbart': 'Breitbart',
    'washpost': 'WashingtonPost',
    'la_times': 'LATimes',
    'fox': 'Fox',
    'cnn': 'CNN',
    'chicago_tribune': 'ChicagoTribune',
    'newyork_post': 'NYPost',
    'redstate': 'RedState',
    'USAtoday': 'USAToday',
    'washexaminer': 'washington examiner',
    'dailycaller': 'DailyCaller',
    'wsj': 'WallStJournal',
    'newsday':'Newsday',
    'startribune': 'StarTribune',
}

def combine_journalist_data():
    data_base_dir = '/nfs/turbo/si-juliame/social-movements/'
    tow_dir = os.path.join(data_base_dir,'journalists-twitter-activity','newsroom_data')
    top10000_file = os.path.join(data_base_dir,'Top10000Journos.csv')
    outlet_files = glob.glob(os.path.join(tow_dir,'*.csv'))
    tow_all_outlet_dfs = []
    for outlet_file in outlet_files:
        outlet_name = os.path.basename(outlet_file).split('.')[0]
        print(outlet_name)
        if outlet_name in org_name_map:
            outlet_name = org_name_map[outlet_name]
        outlet_df = pd.read_csv(outlet_file)
        outlet_df = outlet_df[['username']].drop_duplicates()
        outlet_df['organization'] = outlet_name
        tow_all_outlet_dfs.append(outlet_df)
    tow_df = pd.concat(tow_all_outlet_dfs)
    print(tow_df)

    # Load the top 10000 journalists
    top10000_df = pd.read_csv(top10000_file)
    top10000_df = top10000_df[['username','site']]
    top10000_df = top10000_df.rename(columns={'site':'organization'})
    df = pd.concat([tow_df,top10000_df])
    df = df.drop_duplicates('username')
    df.to_csv(os.path.join(data_base_dir,'all_journalists.csv'),index=False)
    print(df)

def load_journalist_usernames(filename):
    df = pd.read_csv(filename)
    df['username'] = df['username'].str.lower()
    return set(df['username'].tolist())

def load_smo_user_ids(filename):
    df = pd.read_csv(filename)
    df.columns = ['event_organizer','movement','retrieval_id','user_id','username']
    return set(df['user_id'].tolist())


def get_stakeholder_info(row,journalist_usernames,smo_user_ids):
    if row['user_id'] in smo_user_ids:
        return 'smo'
    elif row['screen_name'].lower() in journalist_usernames:
        return 'journalist'
    else:
        return 'other'

def add_stakeholder_labels(full_corpus_filename,out_file,journalist_usernames,smo_user_ids):
    df = pd.read_csv(full_corpus_filename,sep='\t')
    df['stakeholder_group'] = df.apply(lambda row: get_stakeholder_info(row,journalist_usernames,smo_user_ids),axis=1)
    df.to_csv(out_file,sep='\t',index=False)
    # get numbers of each group in stakeholder_group
    print(df['stakeholder_group'].value_counts())




def main():
    data_base_dir = '/nfs/turbo/si-juliame/social-movements/'
    journalist_file = os.path.join(data_base_dir,'all_journalists.csv')
    datasheet_file = os.path.join(data_base_dir,'full_corpus_with_preds_08-02-2023.tsv')
    smo_file = os.path.join(data_base_dir,'accounts_protest_actors_2017-2019.csv')
    out_file = os.path.join(data_base_dir,'full_corpus_with_preds_and_stakeholders_08-02-2023.tsv')

    journalist_usernames = load_journalist_usernames(journalist_file)
    smo_user_ids = load_smo_user_ids(smo_file)
    add_stakeholder_labels(datasheet_file,out_file,journalist_usernames,smo_user_ids)





if __name__ == "__main__":
    main()



