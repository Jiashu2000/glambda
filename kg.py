
import pandas as pd
from entity import Entity
from news import News

# Knowledge Graph Class
output_path = "data_intermediate"

class KG:

    def __init__(self) -> None:
        self.entities = {}
        self.entity_no = 0
        self.news = {}
        self.news_no = 0

    def create_entity_instances(self, entity_path):
        entity_df = pd.read_csv(entity_path, index_col = 0)
        for i in range(len(entity_df)):
            entity_name = entity_df.iloc[i, 0]
            entity_link = entity_df.iloc[i, 1]
            entity_class = entity_df.iloc[i, 2]
            new_entity = Entity(self.entity_no, entity_name, entity_link, entity_class)
            self.entities[entity_name] = new_entity
            self.entity_no += 1
    
    def create_news_instances(self, news_path):
        news_df = pd.read_csv(news_path, index_col = 0)
        for i in range(len(news_df)):
            news_id = news_df.iloc[i, -2]
            news_text = news_df.iloc[i, -1]
            news_title = news_df.iloc[i, 0]
            news_url = news_df.iloc[i, 2]
            news_source_name = news_df.iloc[i, -3]
            new_news = News(news_id, news_text, news_title, news_url, news_source_name)
            self.news[news_id] = new_news
            self.news_no += 1
    
    def assign_entity_to_news(self, parsed_entity_path):
        parsed_entities = pd.read_csv(parsed_entity_path, index_col = 0)
        for news_id, news_instance in self.news.items():
            news_entity_df = parsed_entities.loc[parsed_entities['news_id'] == news_id]
            news_entities = set(news_entity_df['ent_name'])
            for ent_name in news_entities:
                if ent_name in self.entities:
                    news_instance.entities.add(self.entities[ent_name])
    
    def create_relations(self):
        raw_relations = pd.DataFrame(columns = ['news_id', "subject", "relation", "object"])
        relations = pd.DataFrame(columns = ['news_id', "node1", "node2", "relation"])
        for news_id, news_instance in self.news.items():
            news_raw_rels = news_instance.raw_relation_extraction()
            for raw_rel in news_raw_rels:
                new_row = {"news_id": news_id, "subject": raw_rel['subject'], "relation": raw_rel['relation'], "object": raw_rel["object"]}
                raw_relations.loc[len(raw_relations)] = new_row
            
            news_rels = news_instance.filter_relation()
            for rel in news_rels:
                new_row = {"news_id": news_id, "node1": rel['subject'], "node2": rel["object"], "relation": rel['relation']}
                relations.loc[len(relations)] = new_row

        raw_relations.to_csv(output_path +"/raw_relations.csv")
        relations.to_csv(output_path +"/relations.csv")
    
    def create_inner_relations(self):
        inner_relations = pd.DataFrame(columns = ['news_id', "node1", "node2", "relation"])
        for _, news_instance in self.news.items():
            news_inner_rels = news_instance.inner_relation()
            inner_relations = pd.concat([inner_relations, news_inner_rels])
        inner_relations.to_csv(output_path +"/inner_relations.csv")
            

entity_path = "data_intermediate/entity_list.csv"
news_path = "data_intermediate/filter_data.csv"
parsed_entity_path = "data_intermediate/parsed_entities.csv"

kg = KG()
kg.create_entity_instances(entity_path)
kg.create_news_instances(news_path)
kg.assign_entity_to_news(parsed_entity_path)
kg.create_relations()
kg.create_inner_relations()

print(len(kg.news))
news0 = kg.news[0]
print(news0.news_text)
print([e.entity_name for e in news0.entities])
