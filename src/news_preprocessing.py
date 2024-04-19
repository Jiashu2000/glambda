
# Data Preprocessing

import pandas as pd

input_path = "../data_input"
output_path = "../data_intermediate"

# read data
usecols = ['title', 'description', 'url', "source_name"]
data = pd.read_csv(input_path+"/latest_lgbt_news.csv", usecols = usecols)

# select news from credible sources 
selected_news_sources = set(['Advocate.com', 'ABC News', 'Forbes', 'Breitbart News', 'Naturalnews.com', 'DW (English)', 'NBC News', 'BBC News', 'Yahoo Entertainment', 'Scientific American', 'NPR', 'RT', 'ABC News (AU)', 'CBC News', 'CBS News'])

filter_df = data#[data['source_name'].isin(selected_news_sources)]

# drop duplicate news
filter_df = filter_df.drop_duplicates(subset = ['title'], keep = 'first')
filter_df = filter_df.drop_duplicates(subset = ['url'], keep = 'first')
filter_df = filter_df.dropna()
# add a unique news id
filter_df = filter_df.reset_index(drop = True)
filter_df['news_id'] = filter_df.index 
filter_df['news_id'] = filter_df['news_id'].apply(str)

# combine title with description
filter_df['text'] = filter_df['title'] + ". " + filter_df['description']


filter_df.to_csv(output_path + "/filter_data.csv")
