# Clustering


input_path = "../data_intermediate"
output_path = "../data_intermediate"


import pandas as pd
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_lg
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Load Data

usecols = ['news_id', 'title', 'text']
news = pd.read_csv(input_path + "/filter_data.csv", usecols = usecols)

# Preprocessing

# Stopwords
punctuations = string.punctuation
stopwords = list(STOP_WORDS)
custom_stop_words = []  # add customed stop words
for w in custom_stop_words:
    if w not in stopwords:
        stopwords.append(w)

# Tokenization
parser = en_core_web_lg.load()
def spacy_tokenizer(sentence):
    tokens = parser(str(sentence))
    tokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens ]
    tokens = [ word for word in tokens if word not in stopwords and word not in punctuations ]
    tokens = " ".join([i for i in tokens])
    return tokens

# Filter na
news["processed_text"] = news["text"].apply(spacy_tokenizer)
news = news[~news['processed_text'].str.contains("removed")]
news = news[news['processed_text'] != 'nan']

# Vectorization

text = news['processed_text'].values
wordset = set([w for t in text for w in t.split()])

def vectorize(text, maxx_features):
    vectorizer = TfidfVectorizer(max_features=maxx_features)
    X = vectorizer.fit_transform(text)
    return X

max_features = len(wordset)
X = vectorize(text, max_features)

# Dimmension Reduction (Used when the dataset is big and max_features is a large number)

pca = PCA(n_components=0.95, random_state=42)
X_reduced= pca.fit_transform(X.toarray())
X_reduced.shape

# KMeans Clustering
# Hard clustering. Assign each news to one cluster

k = 10 # k is currently fixed at 10
kmeans = KMeans(n_clusters=k, random_state=42, n_init = 'auto')
y_pred = kmeans.fit_predict(X.toarray())
news['cluster'] = y_pred

# Topic Modeling
# Soft clustering. Find n topics for each cluster.

vectorizers = []   
for ii in range(0, 10):
    # Creating a vectorizer for each cluster
    vectorizers.append(CountVectorizer(min_df=2, max_df=0.9, 
                                       stop_words='english', lowercase=True, 
                                       token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}'))

vectorized_data = []
for current_cluster, cvec in enumerate(vectorizers):
    try:
        vectorized_data.append(cvec.fit_transform(news.loc[news['cluster'] == current_cluster, 'processed_text']))
    except Exception as e:
        vectorized_data.append(None)

# number of topics per cluster
num_topics_per_cluster = 3
lda_models = []
for ii in range(0, 10):
    # Latent Dirichlet Allocation Model
    lda = LatentDirichletAllocation(n_components=num_topics_per_cluster, max_iter=10, learning_method='online',verbose=False, random_state=42)
    lda_models.append(lda)


clusters_lda_data = []
for current_cluster, lda in enumerate(lda_models):  
    if vectorized_data[current_cluster] != None:
        clusters_lda_data.append((lda.fit_transform(vectorized_data[current_cluster])))

# Selecting keywords for each topic
def selected_topics(model, vectorizer, top_n=3):
    current_words = []
    keywords = []
    
    for _, topic in enumerate(model.components_):
        words = [(vectorizer.get_feature_names_out()[i], topic[i]) for i in topic.argsort()[:-top_n - 1:-1]]
        for word in words:
            if word[0] not in current_words:
                keywords.append(word)
                current_words.append(word[0])
                
    keywords.sort(key = lambda x: x[1])  
    keywords.reverse()
    return_values = []
    for ii in keywords:
        return_values.append(ii[0])
    return return_values

all_keywords = []
for current_vectorizer, lda in enumerate(lda_models):
    if vectorized_data[current_vectorizer] != None:
        all_keywords.append(selected_topics(lda, vectorizers[current_vectorizer]))
    else:
        all_keywords.append([])


cluster_keywords = pd.DataFrame(columns = ['cluster', 'keywords'])
for cluster, keywords in enumerate(all_keywords):
    kw_str = ', '.join(keywords)
    new_row = {'cluster': cluster, 'keywords': kw_str}
    cluster_keywords.loc[len(cluster_keywords)] = new_row

cluster_keywords.to_csv(output_path + "/cluster_keywords.csv")


news_cluster = pd.merge(news, cluster_keywords, left_on = 'cluster', right_on = 'cluster')
news_cluster['news_id'] = news_cluster['news_id'].astype('int')
news_cluster = news_cluster.sort_values(by = 'news_id')

news_cluster.to_csv(output_path + "/news_cluster.csv")