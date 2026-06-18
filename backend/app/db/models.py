from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    entry_price = Column(Float)
    exit_price = Column(Float)
    order_id = Column(String)
    qty = Column(Integer)
    side = Column(String)
    pnl = Column(Float)
    status = Column(String) # OPEN, CLOSED
    timestamp = Column(DateTime, default=datetime.utcnow)

class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    capital = Column(Float, default=10000.0)
    max_trades = Column(Integer, default=3)
    mode = Column(String, default="MANUAL") # MANUAL or INTELLIGENCE
    trading_mode = Column(String, default="PAPER")
# Database connection - creates trades.db in the project root
engine = create_engine('sqlite:///../trades.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ SQLite Database & Tables Initialized")

if __name__ == "__main__":
    init_db()