from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,  scoped_session

db_string = 'sqlite:///services.db'
engine = create_engine(db_string)

Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
