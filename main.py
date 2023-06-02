from app import app
from database import run_database
import sys


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    run_database()
    app.run()