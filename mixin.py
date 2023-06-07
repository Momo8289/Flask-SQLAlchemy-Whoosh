from whoosh.fields import TEXT, ID, KEYWORD
from whoosh.qparser import QueryParser
import sqlalchemy.sql
from flask_sqlalchemy import SQLAlchemy

from .searcher import WhooshSearcher


class SearchableMixin():
    @classmethod
    def init_search(cls, searcher: WhooshSearcher, db: SQLAlchemy):
        cls.searcher = searcher
        cls.db = db

        cls.db.event.listen(db.session, 'before_commit', cls.before_commit)
        cls.db.event.listen(db.session, 'after_commit', cls.after_commit)

    @classmethod
    def search(cls, field, term, page, per_page=20):
        ix = cls.searcher.get_index(cls)
        with ix.searcher() as searcher:
            parser = QueryParser(field, ix.schema)
            query = parser.parse(term)
            results = searcher.search_page(query, page, pagelen=per_page)
            total = len(results)
            ids = [r["id"] for r in results]

            if total == 0:
                return cls.query.filter(sqlalchemy.sql.false()), 0
            when = []
            for i in range(len(ids)):
                when.append((ids[i], i))

            query = (cls.query.filter(cls.id.in_(ids)).order_by(
                cls.db.case(when, value=cls.id)), total)
            return query


    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                cls.searcher.add_to_index(obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                cls.searcher.add_to_index(obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                cls.searcher.remove_from_index(obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            cls.searcher.add_to_index(obj)
