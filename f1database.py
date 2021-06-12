import f1config
import psycopg2 as dbwrapper

BEST_LAP_STATEMENT_TEMPLATE = """
        INSERT INTO best_lap_times (player, trackid, sessiontypeid, teamid, tireid, time) 
        VALUES ('%s', %d, %d, %d, %d, %f);"""


def connect():
    """
    Tries to connect to a database as defined in the config file. Returns the
    connection object on success
    """

    host = f1config.CONFIG.get("/db/connect/host", "localhost")
    dbname = f1config.CONFIG.get("/db/connect/dbname")
    if not dbname:
        raise ConnectionError("Can't connect to database: no database name defined!")
    username = f1config.CONFIG.get("/db/connect/user")
    if not username:
        raise ConnectionError("Can't connect to database: no user name defined!")
    password = f1config.CONFIG.get("/db/connect/password", "")

    conn = dbwrapper.connect(
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

    data = None
    try:
        cursor = db_connection.cursor()

        cursor.execute(sql)

        data = cursor.fetchall()

        db_connection.commit()
        print("committed")
    except Exception as err:
        print(err)
        db_connection.rollback()
    finally:
        if cursor:
            cursor.close()

    return data


def generate_best_lap_data_sql_statement(name: str, track_id: int, session_type: int,
        team_id: int, tyre_id: int, lap_time: float) -> str:
    return BEST_LAP_STATEMENT_TEMPLATE % (name, track_id, session_type, team_id, tyre_id, lap_time)