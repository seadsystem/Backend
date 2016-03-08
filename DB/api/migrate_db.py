import psycopg2
import psycopg2.extras

# Database user credentials
DATABASE = "seads"
USER = "seadapi"
TABLE = "data_label"

def migrate_db():
    try:
        con = psycopg2.connect(database=DATABASE, user=USER)
        cursor = con.cursor()
        cursor.execute("ALTER TABLE data_label ADD COLUMN classification bool NOT NULL DEFAULT TRUE;")
    except psycopg2.DatabaseError as e:
        print('Database error: %s' % e)
    finally:
        if con:
            con.commit()
            con.close()

migrate_db()