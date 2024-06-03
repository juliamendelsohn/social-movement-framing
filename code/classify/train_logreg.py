import re
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.metrics import f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
import pathlib

def preprocess(text):
	new = text.lower()
	#new = re.sub(r'@\w+','',new)
	new = re.sub(r'https[^ ]*','',new)
	new = re.sub(r'[^@#a-z0-9 ]','',new)
	new = re.sub(r' +',' ',new)
	return new



def load_data(data_file,preprocess=False):
	df = pd.read_csv(data_file,sep='\t')
	df['label'] = df['label'].replace(['pro','neutral/unclear','anti'],[0,1,2])
	if preprocess:
		df['preprocessed_text'] = df['text'].apply(preprocess)
	else:
		df['preprocessed_text'] = df['text']
	return df

def train_model(df,vectorizer):
	train_texts = df['preprocessed_text'].tolist()
	X = vectorizer.fit_transform(train_texts)
	y = df['label'].tolist()
	clf = LogisticRegression(random_state=42,max_iter=10000)
	clf.fit(X,y)
	return clf

def eval_model(df,clf,vectorizer):
	X = vectorizer.transform(df['preprocessed_text'].tolist())
	y = df['label'].tolist()
	preds = clf.predict(X)

	report = pd.DataFrame(classification_report(y,preds,
		labels=[0,1,2],
		target_names=['pro','neutral/unclear','anti'],output_dict=True,zero_division=0)).transpose()
	return report


def get_wrong_predictions(df,clf,vectorizer):
	X = vectorizer.transform(df['preprocessed_text'].tolist())
	y = df['label'].tolist()
	preds = clf.predict(X)
	df['preds'] = preds
	wrong_preds = df[df['label']!=df['preds']]
	return wrong_preds

def print_top10(vectorizer, clf, class_labels):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names_out()
    for i, class_label in enumerate(class_labels):
        top10 = np.argsort(clf.coef_[i])[-20:]
        print("%s: %s" % (class_label,
              " ".join(feature_names[j] for j in top10)))


def main():

	base_data_dir = "/home/juliame/social-movements/stance_data/"
	base_result_dir = "/nfs/turbo/si-juliame/social-movements/stance_logreg_bow_no_preprocess_tfidf_eval/"
	train_datasets = ['majority_agreement_50'] + [f'individual_labels_worker_filter_{i}' for i in [0,33,50,67]]
	eval_dataset = 'majority_agreement_50'
	issues = ['lgbtq','guns','immigration','all_issues']
	models = ['lgbtq','guns','immigration','all_issues']

	for train_dataset in train_datasets:
		for issue in issues:
			for model in models:
				train_file = os.path.join(base_data_dir,train_dataset,f'{model}_train.tsv')
				dev_file = os.path.join(base_data_dir,eval_dataset,f'{issue}_dev.tsv')
				result_file = os.path.join(base_result_dir,eval_dataset,f'{issue}_trained_on_{model}_{train_dataset}_data.tsv')
				pathlib.Path(os.path.join(base_result_dir,eval_dataset)).mkdir(parents=True,exist_ok=True)

				df_train = load_data(train_file)
				df_eval = load_data(dev_file)
				vectorizer = TfidfVectorizer(ngram_range=(1,1),lowercase=True)
				clf = train_model(df_train,vectorizer)
				report = eval_model(df_eval,clf,vectorizer)
				print(eval_dataset,train_dataset,issue,model)
				report.to_csv(result_file,sep='\t')

	# wrong_preds_dfs = []	
	# for dataset in datasets[1:2]:
	# 	for issue in issues:
	# 		for model in models:
	# 			train_file = os.path.join(base_data_dir,dataset,f'{model}_train.tsv')
	# 			dev_file = os.path.join(base_data_dir,dataset,f'{issue}_dev.tsv')
				
	# 			df_train = load_data(train_file)
	# 			df_eval = load_data(dev_file)
	# 			vectorizer = TfidfVectorizer(ngram_range=(1,1),lowercase=True)
	# 			clf = train_model(df_train,vectorizer)
	# 			if issue == model:
	# 				print(issue,model)
	# 				print_top10(vectorizer,clf,[0,1,2])

	# 			wrong_preds = get_wrong_predictions(df_eval,clf,vectorizer).copy()
	# 			wrong_preds['Issue'] = issue
	# 			wrong_preds['Model'] = model
	# 			wrong_preds_dfs.append(wrong_preds)

	# df_wrong = pd.concat(wrong_preds_dfs)
	# df_wrong.to_csv(os.path.join(base_result_dir,'wrong_preds.tsv'),sep='\t',index=False)

				



if __name__ == "__main__":
	main()