from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models here so Base.metadata.create_all() knows them
from app.db.models import Payment 
