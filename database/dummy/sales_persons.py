import bcrypt
from app.auth.models import Sales
from .. import db


# add sales
salesA = Sales(
    username="salesA", 
    name="Suhendra", 
    password=bcrypt.hashpw("sA".encode('utf-8'), bcrypt.gensalt()), 
    email="jpiay40@students.calvin.ac.id", 
    verified=True
)

salesB = Sales(
    username="salesB", 
    name="Siti", 
    password=bcrypt.hashpw("sB".encode('utf-8'), bcrypt.gensalt()), 
    email="cjsonnnnn@gmail.com", 
    verified=False
)

# add to database
db.session.add_all([
    salesA, salesB
])
db.session.commit()

print("HAIIIII")