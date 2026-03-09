import psycopg2
import time
import os
from dotenv import load_dotenv

env = os.getenv("APP_ENV", "dev")

if env == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")
class database_utils:
    # """Database utility class for handling all database operations"""

    @staticmethod
    def _get_connection():
        db_params = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USERNAME"),
            "password": os.getenv("DB_PASSWORD")
        }
        # Enable SSL only for production
        if env == "prod":
            db_params["sslmode"] = "require"

        conn = psycopg2.connect(**db_params)

        return conn

    @staticmethod
    def performeSelectStatement(query, inputParam, logger):
        """Execute SELECT query and return results"""
        cursor = None
        connection = None
        try:
            start_time = time.time()
            connection = database_utils._get_connection()
            cursor = connection.cursor()
            cursor.execute(query, inputParam)
            data = cursor.fetchall()
            elapsed = format(time.time() - start_time, '.2f')
            logger.info(f"Query executed | {len(data)} rows fetched in {elapsed}s | Host: {os.getenv('DB_HOST')}")
            return data
        except psycopg2.Error as e:
            logger.error(f"Database error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def performInsertUpdateDelete(query, inputParam, logger):
        """Execute INSERT/UPDATE/DELETE query"""
        cursor = None
        connection = None
        try:
            start_time = time.time()
            connection = database_utils._get_connection()
            cursor = connection.cursor()
            cursor.execute(query, inputParam)
            connection.commit()
            elapsed = format(time.time() - start_time, '.2f')
            logger.info(f"Query committed in {elapsed}s")
            return 1
        except psycopg2.Error as e:
            logger.error(f"Database error: {str(e)}")
            if connection:
                connection.rollback()
            return 0
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            if connection:
                connection.rollback()
            return 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_city_names_by_prefix(prefix, logger):
        """Get city names matching prefix using parameterized query"""
        cursor = None
        connection = None
        try:
            start_time = time.time()
            connection = database_utils._get_connection()
            cursor = connection.cursor()
            # Use parameterized query to prevent SQL injection
            query = f"SELECT city FROM city_master WHERE city ILIKE '%%{prefix}%%' ORDER BY city"
            cursor.execute(query)
            data = cursor.fetchall()
            elapsed = format(time.time() - start_time, '.2f')
            logger.info(f"City search | {len(data)} cities found in {elapsed}s")
            return [row[0] for row in data]
        except psycopg2.Error as e:
            logger.error(f"Database error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()