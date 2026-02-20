# app/db/base.py
from sqlalchemy.orm import declarative_base

# Create the Base class that models will inherit from
Base = declarative_base()

# DELETE EVERYTHING ELSE BELOW THIS LINE.
# Do NOT import User, Book, etc. here.