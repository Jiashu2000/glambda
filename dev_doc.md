## Glamabda Development Notes v6

### Data Source

1. News data; Google News API
2. Filter news source (news_source_list)
3. Limit SearchIn option to title & description

### Development Steps

1. Data Preprocessing

    - Main:
      - Select only useful columns
      - Add a unique news_id to each news
      - Combine title with description
    - Code: news_preprocessing.py
    - Input: raw_news.csv
    - Output: filter_data.csv

2. Name Entity Recognition Using YODIE

    - Main:
      - API request: (https://cloud.gate.ac.uk/shopfront/displayItem/yodie-en)
    - Code: ner_yodie.py
    - Input: filter_data.csv
    - Output: yodie_ner folder (one json file per news)
    - can only parse 29 news at one time, run this on daily basis.

3. Parse NER Json files

    - Main:
      - Extract entity name, entity link, entity class from json
      - Combine all entities
    - Code: parse_ner_json.py
    - Input: yodie_ner folder
    - Output: parsed_entities.csv

4. Create Entity List

    - Main:
      - Text normalization on entity name
      - Drop duplicate entities
    - Code: create_entity_list.py
    - Input: parsed_entities.csv
    - Output: entity_list.csv
   
5. Relation Extraction Using Standford Core NLP

    - Main:
      - Extract raw relations from news text
    - Code: re_stanford.py
    - Input: filter_data.csv
    - Ouput: raw_relations.csv
   
6. Filter Relations & Transform Relation Node
  
    - Main:
      - Extract nouns from subject and object
      - Match node name to entity.
      - Filter relations with two relevant entities
    - Code: filter_relations.py
    - Input: raw_relations.csv, entity_list.csv
    - Output: transformed_relations.csv
  
7. Clustering & Topic Modeling

    - Main:
      - Data preprocessing (stopwords, tokenization, remove na)
      - Vectorization
      - KMeans clustering (10 clusters)
      - Topic modeling for each cluster (3 topics for each cluster)
    - Code: kmeans_lda.ipynb
    - Input: filter_data.csv
    - Output: cluster_keywords.csv, news_cluster.csv, cluster_keywords.txt
    - To-dos:
      - Use bert topic modeling
      - Add customed stop words 
      - k is set to 10, fixed.
      - cluster keywords should be changed to txt file.

8. Node Graph Info
   
   - Main
   - Code: node_graph_info.py

9. Node Graph Draw

   - Code: node_graph.py

10. Merge Relations & Group Node Information
  
    - Main:
      - Merge semantic relations and statistic relations.
      - Merge cluster node and entity node.
      - Group relevant information for each node.
    - Code: merge_relation_node.py
    - Input: transformed_relations.csv, news_cluster.csv, filter_data.csv, parsed_entities.csv
    - Output: merged_relations.csv, node_info.csv, cluster_entity.csv
  
11. Draw Graph

    - Main:
      - Create knowledge graph
    - Code: knowledge_graph.py


#### To-dos & Product Ideas

1. clustering using bert.
2. add a fixed set of key entities
3. custom stopwords       √
4. presentation (problem statement, architecture) √
5. host aws
6. search box √
7. graph database 
8. select top news for each cluster  √
9. kg: relations not presentable
10. co-occurance
11. add news title before links
12. transformer-based approach for cluser summarization
13. embedding-based model for clustering √
14. use embedding to match entity and relation node