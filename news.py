
# News class

import pandas as pd
from openie import StanfordOpenIE

properties = { 'openie.affinity_probability_cap': 1 / 3,}


class News:

    def __init__(self, news_id, news_text, news_title = None, news_url = None, news_source_name = None) -> None:
        self.news_id = news_id
        self.news_text = news_text
        self.news_title = news_title
        self.news_url = news_url
        self.news_source_name = news_source_name
        self.entities = set()
        self.raw_relations = []
        self.relations = []
    
    def raw_relation_extraction(self):
        with StanfordOpenIE(properties=properties) as client:
            for triple in client.annotate(self.news_text):
                print('|-', triple)
                self.raw_relations.append(triple)
        return self.raw_relations
    
    def filter_relation(self):
        for rel in self.raw_relations:
            if self.relevant_relation(rel):
                self.relations.append(rel)
        return self.relations

    def relevant_relation(self, rel):
        """
        A relation is meaningful if and only if subject and object both have overlapping words with one of the identified entities.
        This criteria is subject to change.
        """
        node1, node2 = rel['subject'], rel['object']
        node1_words = node1.lower().split()
        node2_words = node2.lower().split()
        node1_flag = False
        node2_flag = False
        for entity in self.entities:
            entity_words = set(entity.entity_name.lower().split())
            if (not node1_flag) and (self.number_of_matching_words(entity_words, node1_words) >= 1):
                rel['subject'] = entity.entity_name
                node1_flag = True
            if (not node2_flag) and (self.number_of_matching_words(entity_words, node2_words) >= 1):
                rel['object'] = entity.entity_name
                node2_flag = True
        return node1_flag or node2_flag

    def number_of_matching_words(self, entity_words, node_words):
        match_num = 0
        for w in node_words:
            if w in entity_words:
                match_num += 1
        return match_num
    
    def inner_relation(self):
        inner_rel = pd.DataFrame(columns = ['news_id', 'node1', 'node2', 'relation'])
        entity_list = list(self.entities)
        n = len(entity_list)
        for i in range(n): 
            for j in range(i+1, n):
                node1 = entity_list[i].entity_name 
                node2 = entity_list[j].entity_name
                new_row = {"news_id": self.news_id, "node1": node1, 'node2': node2, "relation": "proximity"}
                inner_rel.loc[len(inner_rel)] = new_row
        return inner_rel

"""
doc = "Pope Francis Calls Surrogate Motherhood ‘Deplorable,’ Calls for Global Ban. The Catholic leader’s stance on surrogacy is likely to roil the LGBT community, of which many members have relied on the practice to have their own children."       
s = News(1, doc)
s.entities = set(['LGBT community',
 'Pope Francis',
 'Surrogate Motherhood',
 'The Catholic leader'])
s.relation_extraction()
"""