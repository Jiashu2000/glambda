
# Entity Class


class Entity:

    def __init__(self, entity_id, entity_name, entity_link = None, entity_class = None) -> None:
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.entity_link = entity_link
        self.entity_class = entity_class
    