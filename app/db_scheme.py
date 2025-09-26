from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

engine = create_engine("postgresql://user:pass@localhost:5432/db")

Base = declarative_base()