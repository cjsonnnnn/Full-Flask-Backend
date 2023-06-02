from app.main.models import Category
from .. import db


# add categories
catA = Category(name="beverages")
catB = Category(name="foods")
catC = Category(name="cleaning product")

# add to database
db.session.add_all([
    catA, catB, catC
])
db.session.commit()