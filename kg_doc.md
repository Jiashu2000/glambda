## Knowledge Graph Development Notes

### Data Source

1. News data; Google News API

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
  
7.  Draw Graph

    - Main:
      - Create knowledge graph
    - Code: draw_graph.py
    - Input: transformed_relations.csv
    - Output: kg.html


#### To-dos:

1. topic modeling new nodes
2. text normalization/wikidata entity matching
3. add a fixed set of key entities
4. front-end add links

#### Product Ideas

1. kg link, host aws, interactive, lead to news
2. search engine box
3. two layers (when, who)
4. present the most important information
5. backend: graph database
