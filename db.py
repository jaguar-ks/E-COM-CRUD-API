from sqlmodel import Session, create_engine

sqlite_file = "./database.db"
sqlite_url = f"sqlite:///{sqlite_file}"

engine = create_engine(sqlite_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
