class SerializableMixin:
    def with_relationships(self, relationships: list[str] | None, data: dict) -> dict:
        if not relationships:
            return data

        for rel_name in relationships:
            if hasattr(self, rel_name):
                rel_data = getattr(self, rel_name)
                if isinstance(rel_data, list):
                    data[rel_name] = [
                        item.to_dict() if hasattr(item, "to_dict") else str(item)
                        for item in rel_data
                    ]
                else:
                    data[rel_name] = (
                        rel_data.to_dict()
                        if hasattr(rel_data, "to_dict") and rel_data
                        else None
                    )
        return data
