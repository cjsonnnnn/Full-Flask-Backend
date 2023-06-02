from sqlalchemy import text
import mysql.connector
from app import app, db
# from .dummy import initialize_dummy_data

# import modules
from . import triggers
from . import initialize_dummy


# to automatically create a new database, in case it does not exist
def create_database():
    # create the database
    conn = mysql.connector.connect(user='root', password='', host='localhost')
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS sales')
    conn.commit()
    conn.close()


# to put the triggers in to database
def create_triggers():
    with db.engine.connect() as con:
        try:
            for trigger in triggers.triggers:
                con.execute(text(trigger))
        except Exception as e:
            pass


# to run database
def run_database():
    with app.app_context():
        create_database()       # to define all orm database
        db.create_all()         # insert those to db, which is mysql
        create_triggers()       # insert triggers to db
        initialize_dummy.initiinitializeDummy()       # initialize some data to the db