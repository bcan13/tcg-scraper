import sqlite3
import datetime
import os
from typing import Tuple
from contextlib import contextmanager


class DatabaseManager:
    """Manages database connections and operations for the companies database."""

    def __init__(self, db_path: str = None):
        """Initialize the database manager with a specific path or the default."""
        self.db_path = db_path or os.path.join(
            "core", "database", "companies.db"
        )
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        with self.get_connection() as (conn, cursor):
            # Create companies_seen table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies_seen(
                    company_name TEXT PRIMARY KEY,
                    website TEXT,
                    description TEXT,
                    job_type TEXT,
                    size TEXT,
                    location TEXT,
                    date_seen DATE
                )
            """)

            # Create companies_sent table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies_sent(
                    contactee_name TEXT,
                    status TEXT,
                    company_name TEXT PRIMARY KEY,
                    website TEXT,
                    description TEXT,
                    job_type TEXT,
                    size TEXT,
                    location TEXT,
                    contact_name TEXT,
                    email TEXT,
                    date_sent DATE
                )
            """)

    @contextmanager
    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Get a database connection and cursor as a context manager."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            yield conn, cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()


# Create a singleton instance of the database manager
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create the database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def add_company_seen(
    company_name: str,
    description: str,
    job_type: str,
    size: str,
    location: str,
    website: str,
) -> bool:
    """Add a company to the companies_seen table."""
    db = get_db_manager()
    date_seen = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        with db.get_connection() as (conn, cursor):
            cursor.execute(
                """
                INSERT OR IGNORE INTO companies_seen 
                (company_name, description, job_type, size, location, website, date_seen)
                VALUES (?,?,?,?,?,?,?)
            """,
                (
                    company_name,
                    description,
                    job_type,
                    size,
                    location,
                    website,
                    date_seen,
                ),
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error adding company to seen list: {e}")
        return False


def add_company_sent(
    contactee_name: str,
    status: str,
    company_name: str,
    description: str,
    job_type: str,
    size: str,
    location: str,
    website: str,
    contact_name: str,
    email: str,
) -> bool:
    """Add a company to the companies_sent table."""
    db = get_db_manager()
    date_sent = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        with db.get_connection() as (conn, cursor):
            cursor.execute(
                """
                INSERT OR IGNORE INTO companies_sent 
                (contactee_name, status, company_name, description, job_type, size, 
                location, website, contact_name, email, date_sent)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    contactee_name,
                    status,
                    company_name,
                    description,
                    job_type,
                    size,
                    location,
                    website,
                    contact_name,
                    email,
                    date_sent,
                ),
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error adding company to sent list: {e}")
        return False


def company_seen_before(company_name: str) -> bool:
    """Check if a company has been seen or contacted before."""
    db = get_db_manager()

    try:
        with db.get_connection() as (conn, cursor):
            cursor.execute(
                """
                SELECT * FROM companies_seen WHERE company_name = ?
                """,
                (company_name,),
            )
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error checking if company seen before: {e}")
        return False
