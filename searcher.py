import os

from whoosh.fields import Schema
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter


class WhooshSearcher:
    def __init__(self, app):
        self._index_path = app.config["WHOOSH_INDEX_PATH"]

    def _check_index_exists(self, name):
        return os.path.exists(os.path.join(self._index_path, name))

    def _create_index(self, name: str, searchables: dict):
        schema = Schema()
        os.mkdir(self._index_path+name)
        ix = create_in(os.path.join(self._index_path, name), schema)
        writer = AsyncWriter(ix)
        for field_name, type in searchables.items():
            writer.add_field(field_name, type)
        writer.commit()
        return ix

    def get_index(self, obj):
        if self._check_index_exists(name := obj.__tablename__):
            return open_dir(os.path.join(self._index_path, name))
        else:
            return self._create_index(name, obj.__searchable__)

    def add_to_index(self, obj):
        ix = self.get_index(obj)
        writer = AsyncWriter(ix)
        vals = {}
        for field in obj.__searchable__.keys():
            vals[field] = getattr(obj, field)

        writer.update_document(**vals)
        writer.commit()

    def remove_from_index(self, obj):
        ix = self.get_index(obj)
        writer = AsyncWriter(ix)
        writer.delete_by_term("id", obj.id)
        writer.commit()