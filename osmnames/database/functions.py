import os
import time
import psycopg2

from subprocess import check_call
from osmnames import settings
from osmnames import logger

log = logger.setup(__name__)


def psql_exec(filepath, user=settings.get("DB_USER"), cwd=""):
    check_call([
            "psql",
            "--username={}".format(user),
            "--dbname={}".format(settings.get("DB_NAME")),
            "--file={}/{}".format(cwd, filepath)
        ]
    )


def exec_sql_from_file(filename, user=settings.get("DB_USER"), database=settings.get("DB_NAME"), cwd=""):
    file_path = "{}/{}".format(cwd, filename)
    connection = psycopg2.connect(user=user, dbname=database)
    connection.set_session(autocommit=True)
    log.info("start executing sql file {}".format(filename))
    connection.cursor().execute(open(file_path, "r").read())
    log.info("finished executing sql file {}".format(filename))


def exec_sql(sql, user=settings.get('DB_USER'), database=settings.get('DB_NAME')):
    connection = psycopg2.connect(user=user, dbname=database)
    connection.set_session(autocommit=True)
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor


def exists(query, user=settings.get('DB_USER'), database=settings.get('DB_NAME')):
    return exec_sql("SELECT EXISTS({});".format(query), user, database).fetchone()[0]


def count(query, user=settings.get('DB_USER'), database=settings.get('DB_NAME')):
    return exec_sql(query, user, database).fetchone()[0]


def vacuum_database():
    log.info("start vacuum database")
    exec_sql('VACUUM ANALYZE')
    log.info("finished vacuum database")


def wait_for_database():
    while os.system("psql --username=postgres postgres -c 'select 1' > /dev/null 2>&1"):
        print("waiting for postgresql")
        time.sleep(2)
