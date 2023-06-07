# Flask-SQLAlchemy-Whoosh
A simple and easy to use Flask extension to add full text search to your SQLAlchemy models using the Whoosh search engine.

### Installing
`$ pip install Flask-SQLAlchemy-Whoosh`

### Setup
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_whoosh.searcher import WhooshSearcher
from flask_sqlalchemy_whoosh.mixin import SearchableMixin
from whoosh.fields import ID, TEXT, NUMERIC


app = Flask(__name__)
db = SQLAlchemy(app)
search = WhooshSearcher(app)

# If you want to use the SearchableMixin
SearchableMixin.init_search(search, db)


class Product(SearchableMixin, db.Model):
    __tablename__ = "product"
    # __searchable__ is needed to tell the searcher what to index
    # For documentation on the specifics of each field, refer to the Whoosh documentation
    # https://whoosh.readthedocs.io/en/latest/schema.html
    __searchable__ = {
        "id": ID(stored=True, unique=True),
        "name": TEXT(stored=True),
        "desc": TEXT,
        "price": NUMERIC
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String),
    desc = db.Column(db.String),
    price = db.Column(db.Integer)

```

