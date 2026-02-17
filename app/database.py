import psycopg2
import time
from urllib.parse import urlparse


# # Database Configuration - Universal
# DB_USERNAME = "postgres"
# DB_PASSWORD = "123456"
# DB_HOST = "localhost"
# DB_PORT = "5432"
# DB_NAME = "AstrologyTravelDB"

# Database Configuration - Universal
DB_USERNAME = "postgres"
DB_PASSWORD = "brFjUCrJSeDVLnVAxfVCkTpuHjXUEecW"
DB_HOST = "postgres.railway.internal"
DB_PORT = "5432"
DB_NAME = "railway"

class database_utils:
    """Database utility class for handling all database operations"""

    @staticmethod
    def _get_connection():

        database_url = "postgresql://postgres:brFjUCrJSeDVLnVAxfVCkTpuHjXUEecW@postgres.railway.internal:5432/railway"

        if not database_url:
            raise ValueError("DATABASE_URL is not set")

        result = urlparse(database_url)

        return psycopg2.connect(
            database=result.path[1:],  # remove leading '/'
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            sslmode="require"  # 🔥 Required for Railway
        )

    # @staticmethod
    # def _get_connection():
    #     """Create and return a database connection"""
    #     return psycopg2.connect(
    #         user=DB_USERNAME,
    #         password=DB_PASSWORD,
    #         host=DB_HOST,
    #         port=DB_PORT,
    #         database=DB_NAME
    #     )

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
            logger.info(f"Query executed | {len(data)} rows fetched in {elapsed}s | Host: {DB_HOST}")
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