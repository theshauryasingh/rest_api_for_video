from sqlalchemy import create_engine, MetaData

# Example database URL, replace with your own
DATABASE_URL = "sqlite:///app.db"
engine = create_engine(DATABASE_URL)

def truncate_all_tables():
    meta = MetaData()
    meta.reflect(bind=engine)
    
    with engine.connect() as conn:
        trans = conn.begin()  # Start a transaction
        for table in reversed(meta.sorted_tables):  # Reverse to maintain foreign key constraints
            conn.execute(table.delete())  # Equivalent to "DELETE FROM table"
        trans.commit()

truncate_all_tables()
print("All tables truncated.")
