from database import run_database
from app import app
import sys


if __name__ == "__main__":
    sys.dont_write_bytecode = True  # to avoid generating .pyc files
    run_database()
    app.run()
