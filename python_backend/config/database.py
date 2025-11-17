"""
Database connection pool management
"""
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Generator
from .settings import get_settings

settings = get_settings()

# Connection pool
connection_pool: pool.SimpleConnectionPool | None = None


def init_pool():
    """Initialize the database connection pool"""
    global connection_pool
    
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # minconn
            settings.database_pool_size,  # maxconn
            settings.database_url
        )
        print(f"Database pool created with {settings.database_pool_size} connections")


def close_pool():
    """Close all connections in the pool"""
    global connection_pool
    
    if connection_pool is not None:
        connection_pool.closeall()
        connection_pool = None
        print("Database pool closed")


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    if connection_pool is None:
        init_pool()
    
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def test_connection():
    """Test database connectivity"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            print(f"Database connection test successful: {result}")
            return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        raise
