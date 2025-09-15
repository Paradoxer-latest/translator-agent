# config/database.py

import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("database")

DB_URL = os.getenv("DB_URL") or "sqlite:///./app.db"

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    try:
        # If a Declarative Base is defined (e.g., models/base.py), create tables.
        try:
            from models.base import Base  # type: ignore
            # Ensure models are imported so they register with Base.metadata
            from models.user import User  # noqa: F401

            Base.metadata.create_all(bind=engine)
        except Exception:
            # If no Base is available, at least verify the connection.
            with engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")

        logger.info("Database connected using SQLAlchemy")
    except SQLAlchemyError as exc:
        logger.exception("Error while connecting to DB: %s", exc)
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()