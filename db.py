import mysql.connector
from mysql.connector import Error
import json
import random
import datetime
import time
from dateutil.relativedelta import relativedelta

pw = 'REDACTED'
db_name = 'guids'


def connect_to_server(host_name, user_name, password, db_name):
    """Connects to database with specified credentials"""

    connection = None

    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=password,
            database=db_name
        )
        print("Connection Successful")

    except Error as err:
        print(f"Error: '{err}'")

    return connection


def create_database(connection, name):
    """Creates a database with specified name if one does not already exist."""

    query = f"CREATE DATABASE {name}"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


def execute_query(connection, query):
    """Executes specified query on connection object."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
        return Error
    except Error as err:
        print(f"Error: '{err}'")
        return err


def create(guid, input):
    """Create a new entry in the database"""

    connection = connect_to_server("localhost", "root", pw, db_name)

    obj = json.loads(input)
    obj['guid'] = guid

    if obj['guid'] is None:
        obj['guid'] = generate_guid()

    else:
        valid = validate_guid(obj['guid'])

        if not valid:
            print('Invalid GUID. Must be 32 hexadecimal characters, all uppercase.')
            return

    if 'expiration' not in obj.keys():
        obj['expiration'] = datetime.datetime.now() + relativedelta(days=+30)
        obj['expiration'] = int(time.mktime(obj['expiration'].timetuple()))

    query = f"""
    INSERT INTO guids VALUES
    ('{obj['guid']}', '{obj['expiration']}', '{obj['user']}')
    """
    execute_query(connection, query)

    return json.dumps(obj)


def validate_guid(guid):
    """Validate that a guid is 32 hexadecimal characters and all uppercase."""
    if len(guid) != 32:
        return False
    return guid.isupper()


def generate_guid():
    """Randomly generate a GUID if one is not provided."""
    random.seed()
    hex = '0123456789ABCDEF'
    guid = ''

    for i in range(32):
        num = random.randint(0, len(hex)-1)
        guid += hex[num]

    return guid


def read_query(connection, query):
    """Performs a read query on database connection object"""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


def read_guid(guid):
    """Performs a read query to search for specific guid. If successful return a json object."""

    connection = connect_to_server("localhost", "root", pw, db_name)
    query = f"""
    SELECT * FROM guids 
    where guid = '{guid}';
    """
    result = read_query(connection, query)

    if result:
        formatted = dict.fromkeys(['guid', 'expiration', 'user'])
        formatted['guid'] = result[0][0]
        formatted['expiration'] = result[0][1]
        formatted['user'] = result[0][2]
        return json.dumps(formatted)


def update_guid_metadata(guid, input):
    """Receives an input and updates the metadata for it's corresponding GUID to match that of the object.
    If expiration or user are empty they will not be updated. If both fields are empty no updates occur."""

    connection = connect_to_server("localhost", "root", pw, db_name)
    obj = json.loads(input)
    obj['guid'] = guid

    if 'expiration' not in obj.keys() and 'user' not in obj.keys():
        print('No new data was inputted')
        return

    elif 'expiration' not in obj.keys():
        query = f"""
        UPDATE guids
        SET user = '{obj['user']}'
        WHERE guid='{obj['guid']}'
        """

    elif 'user' not in obj.keys():
        query = f"""
        UPDATE guids
        SET expire= '{obj['expiration']}'
        WHERE guid='{obj['guid']}'
        """

    else:
        query = f"""
        UPDATE guids
        SET expire = '{obj['expiration']}', 
        user = '{obj['user']}'
        WHERE guid='{obj['guid']}'
        """

    execute_query(connection, query)
    return json.dumps(obj)


def delete(guid):
    """Removes object with matching GUID to user input"""

    connection = connect_to_server("localhost", "root", pw, db_name)

    guid = guid

    query = f"""
    DELETE FROM guids
    WHERE guid='{guid}'
    """

    execute_query(connection, query)
