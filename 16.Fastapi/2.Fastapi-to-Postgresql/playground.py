# Postgresql URL - postgresql://postgres:password@localhost:5432/database_name
"""
Python will interact with postgresql without any fastapi endpoint
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Column, String, Integer
from sqlalchemy.orm import DeclarativeBase, sessionmaker



load_dotenv()

# getting url from env
database_url = os.getenv("DATABASE_URL")
print(database_url)

# the road to the database
engine = create_engine(database_url)
with engine.connect() as connection:
    version = connection.execute(text("SELECT version()")).scalar()
    print(f"Connected to postgresql {version.split(",")[0]}")

#.all() -> every row
#.first() -> only the first row
#.scalar() -> only the first value of the first row

"""
DeclarativeBase is the Parent class from SQLALchemy that turn a normal python class into a database table

Declartive : You declare(describe) what a table looks like
Base       : It's the Parent class everything else built on top of this.
"""
class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "student_data"
    id      = Column(String, primary_key=True)
    name    = Column(String(50), nullable=False)
    age     = Column(Integer, nullable=False)
    course  = Column(String(50), nullable=False)
    marks   = Column(Integer, nullable=False)
    email   = Column(String, unique=True, nullable=False)  


#bind=engine -> every session travels to this road
Base.metadata.create_all(bind=engine)
print("Table ready...")

#Step 4: Session = One Visit, Open, do work, commit, close
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

if db.get(StudentDB, "S001") is None:
    db.add(StudentDB(id="S001",
                     name="Arin Sharma",
                     age=23,
                     course = "AI Engineering",
                     marks=94,
                     email="arinsharma.research@gmail.com"))
    db.commit()

#Read it Back
for i in db.query(StudentDB).all():
    print(i.id, i.name, i.age, i.marks, i.course, i.email)

# Update the data
data = db.get(StudentDB, "S001")
data.course = "AI Scientist"
db.commit()