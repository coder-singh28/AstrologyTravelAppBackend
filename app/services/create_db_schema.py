import os
import psycopg2
from dotenv import load_dotenv
from app.database import database_utils
import csv
from pathlib import Path

env = os.getenv("APP_ENV", "dev")
if env == "prod":
    load_dotenv("../../.env.prod")
else:
    load_dotenv("../../.env.dev")


class DatabaseSchemaCreator:
    """Class to create database schema and load initial data"""

    def create_tables(self):
        conn = database_utils._get_connection()
        cursor = conn.cursor()

        # SQL for creating tables
        sql = """
        
        CREATE TABLE IF NOT EXISTS public.audit_logs_details (
            id bigserial PRIMARY KEY,
            user_id int8 NOT NULL,
            session_token text NOT NULL,
            event_name text NOT NULL,
            description text NOT NULL,
            created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamptz DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS public.city_master (
            city varchar(50),
            lat varchar(50),
            long varchar(50),
            country varchar(50),
            iso2 varchar(50),
            state varchar(50)
        );
        
        CREATE TABLE IF NOT EXISTS public.session_details (
            id bigserial PRIMARY KEY,
            user_id int8 NOT NULL,
            email varchar(255) NOT NULL,
            session_token text NOT NULL,
            expires_at timestamptz NOT NULL,
            created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamptz DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS public.trip_details (
            trip_id serial PRIMARY KEY,
            user_id int4 NOT NULL,
            source_city varchar(100) NOT NULL,
            destination_city varchar(100) NOT NULL,
            travel_date date NOT NULL,
            departure_time time NOT NULL,
            predict_travel_response jsonb,
            status varchar(20) DEFAULT 'PLANNED',
            created_at timestamp DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS public.users_details (
            id bigserial PRIMARY KEY,
            email varchar(255) NOT NULL UNIQUE,
            full_name varchar(255),
            mobile_no varchar(15) UNIQUE,
            dob varchar(255),
            tob varchar(255),
            birth_place varchar(255),
            is_active bool DEFAULT true,
            is_deleted bool DEFAULT false,
            created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamptz DEFAULT CURRENT_TIMESTAMP
        );
        
        """

        try:
            cursor.execute(sql)
            conn.commit()
            print("✅ All tables created successfully")

        except Exception as e:
            print("❌ Error creating tables:", e)

        finally:
            cursor.close()
            conn.close()


    def load_csv_data(self):
        conn = database_utils._get_connection()
        cursor = conn.cursor()


        BASE_DIR = Path(__file__).resolve().parents[2]
        csv_file_path = BASE_DIR / "city_master.csv"

        # Load CSV into city_master
        # csv_file_path = "../../city_master.csv"

        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                cursor.execute(
                    """
                    INSERT INTO city_master (city, lat, long, country, iso2, state)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row["city"],
                        row["lat"],
                        row["long"],
                        row["country"],
                        row["iso2"],
                        row["state"]
                    )
                )

        conn.commit()

        print("✅ City data loaded successfully")

        cursor.close()
        conn.close()