
# Data Preprocessing

import pandas as pd

input_path = "data_input"
output_path = "data_intermediate"

# read data
usecols = ['title', 'description', 'url', 'source_id', "source_name"]
data = pd.read_csv(input_path+"/raw_news.csv", usecols = usecols)

# select news from credible sources 
data = data[~data['source_id'].isna()]

# add a unique news id
data = data.reset_index(drop = True)
data['news_id'] = data.index 
data['news_id'] = data['news_id'].apply(str)

# combine title with description
data['text'] = data['title'] + ". " + data['description']

data.to_csv(output_path + "/filter_data.csv")
