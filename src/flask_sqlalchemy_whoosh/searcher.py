import os

from whoosh.fields import Schema
from whoosh.index import create_in, open_dir, FileIndex
from whoosh.writing import AsyncWriter
from flask_sqlalchemy.model import Model


class WhooshSearcher:
    def __init__(self, app):
        if app is not None:
            self.init_app(app)
        

    def init_app(self, app):
        self._index_path = app.config["WHOOSH_INDEX_PATH"] or "./whoosh"

    def _check_index_exists(self, name):
        return os.path.exists(os.path.join(self._index_path, name))

    def _create_index(self, name: str, searchables: dict):
        schema = Schema()
        os.mkdir(os.path.join(self._index_path, name))
        # Create the search index
        ix = create_in(os.path.join(self._index_path, name), schema)
        writer = AsyncWriter(ix)
        for field_name, type in searchables.items():
            writer.add_field(field_name, type)
        writer.commit()
        return ix

    def get_index(self, obj: Model) -> FileIndex:
        """Gets the index for the given object, creating one if it does not exist already."""
        if self._check_index_exists(name := obj.__tablename__):
            return open_dir(os.path.join(self._index_path, name))
        else:
            return self._create_index(name, obj.__searchable__)

    def add_to_index(self, obj: Model):
        """Adds a database object to the index"""
        ix = self.get_index(obj)
        writer = AsyncWriter(ix)
        vals = {}
        for field in obj.__searchable__.keys():
            vals[field] = getattr(obj, field)

        writer.update_document(**vals)
        writer.commit()

    def remove_from_index(self, obj: Model):
        """Removes a database object from the index"""
        ix = self.get_index(obj)
        writer = AsyncWriter(ix)
        writer.delete_by_term("id", obj.id)
        writer.commit()