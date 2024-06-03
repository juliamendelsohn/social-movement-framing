import os
import csv
import random

#/nfs/turbo/si-juliame/annotation-sample-bozarth-keyword-tweets
#Collect the tweets from the sample files with a start line and end line range
#Add movement and movement month to the tweet line
#Join all movements and write to a single file

#Read lines from annotation_chunks.txt and returns info for last line
def read_annotation_log_file(annotation_log_file):
    with open(annotation_log_file,'r') as f:
        for row in f:
            date,start_index,end_index = row.split(' ')
        return date,start_index,end_index
            

def get_chunk(data_dir,movements,start_index,end_index):
    samples = []
    for movement in movements:
        movement_month_files = [d for d in os.listdir(data_dir) if d.startswith(movement)]
        for movement_month_file in movement_month_files:
            filename = os.path.join(data_dir,movement_month_file)
            with open(filename,'r') as f:
                reader = csv.reader(f,delimiter='\t')
                next(reader,None) #skip header
                for i,row in enumerate(reader):
                    if i >= int(start_index) and i <= int(end_index):
                        row.append(movement)
                        row.append(movement_month_file)
                        samples.append(row)
    samples = random.sample(samples,len(samples))
    return samples


def write_chunk(out_dir,samples,annotation_date):
    with open(os.path.join(out_dir,annotation_date + '.tsv'),'w') as f:
        writer = csv.writer(f,delimiter='\t')
        writer.writerow(["created_at","id_str", "text","movement","movement_month"])
        for row in samples:
            writer.writerow(row)

def main():
    data_dir = '/nfs/turbo/si-juliame/social-movements/annotation-sample-bozarth-keyword-tweets/'
    out_dir = os.path.join(data_dir,'annotation_chunks')
    if os.path.exists(out_dir) == False:
        os.mkdir(out_dir)
    annotation_log_file = 'annotation_chunks.txt'
    movements = ['guns','immigration','lgbtq']
    date,start_index,end_index = read_annotation_log_file(annotation_log_file)
    print(date,start_index,end_index)
    samples = get_chunk(data_dir,movements,start_index,end_index)
    write_chunk(out_dir,samples,date)
    


if __name__ == "__main__":
    main()