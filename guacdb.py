#!/usr/bin/env python

import os
import psycopg2
import sys
import uuid
import hashlib

def db_connect():

    # Ensure postgres db is connectable
    if os.environ.get('POSTGRES_HOST'):
        POSTGRES_HOST =  os.environ['POSTGRES_HOST']
    else:
        POSTGRES_HOST = 'postgres'

    if os.environ.get('POSTGRES_USER'):
        POSTGRES_USER =  os.environ['POSTGRES_USER']
    else:
        sys.exit(255)

    if os.environ.get('POSTGRES_PASSWORD'):
        POSTGRES_PASSWORD =  os.environ['POSTGRES_PASSWORD']
    else:
        sys.exit(255)

    if os.environ.get('POSTGRES_DATABASE'):
        POSTGRES_DATABASE =  os.environ['POSTGRES_DATABASE']
    else:
        POSTGRES_DATABASE = 'guacamole_db'

    conn_string = "host="+ POSTGRES_HOST +" port="+ "5432" + \
                    " dbname="+ POSTGRES_DATABASE + \
                    " user=" + POSTGRES_USER + \
                    " password="+ POSTGRES_PASSWORD

    db_conn = psycopg2.connect(conn_string)

    return db_conn


def _get_user_identity(username):

    db_conn = db_connect()
    cursor = db_conn.cursor()

    # Execute a command: this creates a new table

    cursor.execute("SELECT entity_id from guacamole_entity where name=%s;", (username,))
    entity_id =  cursor.fetchone()
    # Make the changes to the database persistent
    db_conn.commit()

    # Close communication with the database
    cursor.close()
    db_conn.close()

    return entity_id


def add_user(username, password):
    db_conn = db_connect()
    cursor = db_conn.cursor()

    salt = str(uuid.uuid4()).replace("-", "") + str(uuid.uuid4()).replace("-", "")
    password_hash = hashlib.sha256(''.join((password, salt)).encode('UTF-8')).hexdigest()
    print(password_hash)

    entity_id = _get_user_identity(username)
    if entity_id is None:
        msg = 'Did not receive entity id for user: {0} - adding user'.format(username,)
        print(msg)

        # add user to entity table
        cursor.execute("INSERT INTO guacamole_entity (name, type) VALUES (%s, 'USER');", (username,))
        entity_id = _get_user_identity(username)

        cursor.execute("INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) \
                        SELECT entity_id, decode(%s, 'hex'), decode(%s, 'hex'), CURRENT_TIMESTAMP \
                        FROM guacamole_entity WHERE name = %s AND guacamole_entity.type = 'USER';", (password_hash, salt, username,))
    else:
        msg = 'Retrieved entity id for user: {0} id: {1}'.format(username, entity_id[0])
        print(msg)

        # Update passowrd entry

    # Make the changes to the database persistent
    db_conn.commit()

    # Close communication with the database
    cursor.close()
    db_conn.close()

    return True


def create_connection(hostname, username, password, protocol="rdp", port="3389"):

    name = hostname

    db_conn = db_connect()
    cursor = db_conn.cursor()

    # Need to check if the hostname already exists - then we are just udpdating - Determine the connection_id
    cursor.execute("SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;", (hostname,))
    connection_id = cursor.fetchone()

    if connection_id is None:
        msg = 'Adding new connection by name: {0}'.format(name)
        print(msg)

        cursor.execute("INSERT INTO guacamole_connection (connection_name, protocol) VALUES (%s, %s);", (name, protocol))

        # Now Determine the connection_id
        cursor.execute("SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;", (name,))
        connection_id = cursor.fetchone()

        # Update entry
        cursor.execute("INSERT INTO guacamole_connection_parameter VALUES (%s, 'hostname', %s);", (connection_id[0], hostname,))
        cursor.execute("INSERT INTO guacamole_connection_parameter VALUES (%s, 'port', %s);", (connection_id[0], port,))
        cursor.execute("INSERT INTO guacamole_connection_parameter VALUES (%s, 'username', %s);", (connection_id[0], username,))
        cursor.execute("INSERT INTO guacamole_connection_parameter VALUES (%s, 'password', %s);", (connection_id[0], password,))
    else:
        msg = 'Connection ID already exists for {0} id is:{1}'.format(name, connection_id[0])
        print(msg)

        print("Updating connection params")
        # Update entry
        cursor.execute("UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='hostname';", (hostname, connection_id[0],))
        cursor.execute("UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='port';", (port, connection_id[0],))
        cursor.execute("UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='username';", (username, connection_id[0],))
        cursor.execute("UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='password';", (password, connection_id[0],))

    # Make the changes to the database persistent
    db_conn.commit()

    # Close communication with the database
    cursor.close()
    db_conn.close()

    return True


def main():
    print("Starting Guacamole Broker")

    create_connection(hostname='desktop', username='user', password='KL3ECRd9dd68xFsZ')

    add_user(username='user', password='password')

if __name__ == '__main__':
    main()


