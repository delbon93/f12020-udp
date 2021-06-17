import config
import psycopg2

BEST_LAP_STATEMENT_TEMPLATE = """
INSERT INTO best_lap_times (player, trackid, sessiontypeid, teamid, tireid, time) 
VALUES ('%s', %d, %d, %d, %d, %f);
""".lstrip().rstrip().replace("\n", " ")


def connect():
    """
    Tries to connect to a database as defined in the config file. Returns the
    connection object on success
    """

    host = config.CONFIG.get("/db/connect/host", "localhost")
    dbname = config.CONFIG.get("/db/connect/dbname")
    if not dbname:
        raise ConnectionError("Can't connect to database: no database name defined!")
    username = config.CONFIG.get("/db/connect/user")
    if not username:
        raise ConnectionError("Can't connect to database: no user name defined!")
    password = config.CONFIG.get("/db/connect/password", "")

    conn = psycopg2.connect(
        host=host,
        database=dbname,
        user=username,
        password=password,
    )
    return conn


def disconnect(db_connection):
    """
    Closes the connection to the database
    """

    db_connection.close()


def transaction(db_connection, sql: str):
    """
    Executes a sql transaction on the database and returns query results
    """

    try:
        cursor = db_connection.cursor()

        cursor.execute(sql)

        db_connection.commit()
    except Exception as err:
        print(err)
        db_connection.rollback()
    finally:
        if cursor:
            cursor.close()


def generate_best_lap_data_sql_statement(data: tuple) -> str:
    return BEST_LAP_STATEMENT_TEMPLATE % data
