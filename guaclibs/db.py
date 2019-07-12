import os
import psycopg2
import sys
import uuid
import hashlib

class GuacDatabaseAccess():

    def __init__(self):
        
        print("Database Connecting")

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

        # self.db_conn = psycopg2.connect(conn_string)
        self.db_conn = "test"

    def test(self):

        return "test success"


    def disconnect(self):

        self.db_conn.commit()
        self.db_conn.close()


    def _get_user_id(self, entity_id):

        cursor = self.db_conn.cursor()

        # Execute a command: this creates a new table

        cursor.execute("SELECT user_id from guacamole_user where entity_id=%s;", (entity_id,))
        user_id =  cursor.fetchone()
        
        # Close communication with the database
        cursor.close()

        return user_id


    def _get_user_identity(self, username):

        cursor = self.db_conn.cursor()

        # Execute a command: this creates a new table
        cursor.execute("SELECT entity_id from guacamole_entity where name=%s;", (username,))
        entity_id =  cursor.fetchone()
        
        # Make the changes to the database persistent
        self.db_conn.commit()

        # Close communication with the database
        cursor.close()

        return entity_id


    def _get_connection_id(self, hostname):

        cursor = self.db_conn.cursor()

        cursor.execute("SELECT connection_id from guacamole_connection where connection_name=%s;", (hostname,))
        connection_id =  cursor.fetchone()

        # Make the changes to the database persistent
        self.db_conn.commit()

        # Close communication with the database
        cursor.close()

        return connection_id


    def add_user(self, username, password):

        cursor = self.db_conn.cursor()

        # ensure salt hash is uppercase when stored in postgres - guacamole client requires this - NFI
        salt = uuid.uuid4()
        salt_hash = hashlib.sha256(salt.bytes).hexdigest()
        salt_hash_upper = salt_hash.upper()
        password_hash = hashlib.sha256(''.join((password, salt_hash_upper)).encode('UTF-8')).hexdigest()
        print(salt_hash_upper)
        print(password_hash)

        entity_id = self._get_user_identity(username)
        if entity_id is None:
            msg = 'Did not receive entity id for user: {0} - adding user'.format(username,)
            print(msg)

            # add user to entity table
            cursor.execute("INSERT INTO guacamole_entity (name, type) VALUES (%s, 'USER');", (username,))
            entity_id = self._get_user_identity(username)

            cursor.execute("INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) \
                            SELECT entity_id, decode(%s, 'hex'), decode(%s, 'hex'), CURRENT_TIMESTAMP \
                            FROM guacamole_entity WHERE name = %s AND guacamole_entity.type = 'USER';", (password_hash, salt_hash, username,))

            cursor.execute("INSERT INTO guacamole_user_permission (entity_id, affected_user_id, permission) \
                            SELECT guacamole_entity.entity_id, guacamole_user.user_id, permission::guacamole_object_permission_type \
                            FROM (VALUES (%s, %s, 'READ')) permissions (username, affected_username, permission) \
                            JOIN guacamole_entity          ON permissions.username = guacamole_entity.name AND guacamole_entity.type = 'USER' \
                            JOIN guacamole_entity affected ON permissions.affected_username = affected.name AND guacamole_entity.type = 'USER' \
                            JOIN guacamole_user            ON guacamole_user.entity_id = affected.entity_id;", (username,username,))

        else:
            msg = 'Retrieved entity id for user: {0} id: {1}'.format(username, entity_id[0])
            print(msg)

            # Update password entry

        # Make the changes to the database persistent
        self.db_conn.commit()

        # Close communication with the database
        cursor.close()

        return True


    def create_connection(self, hostname, username, password, protocol="rdp", port="3389"):

        name = hostname
        cursor = self.db_conn.cursor()

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
        self.db_conn.commit()

        # Close communication with the database
        cursor.close()

        return True


    def join_connection_to_user(self, username, hostname):
        
        cursor = self.db_conn.cursor()

        entity_id = self._get_user_identity(username)
        connection_id = self._get_connection_id(hostname)

        cursor.execute("SELECT entity_id from guacamole_connection_permission where entity_id=%s AND connection_id=%s;", (entity_id, connection_id,))
        connection_map_exists = cursor.fetchone()

        if connection_map_exists is None:
            cursor.execute("INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission) \
                            VALUES (%s, %s, 'READ');", (entity_id, connection_id,))
        else:
            print("Connection map already exists")

        # Make the changes to the database persistent
        self.db_conn.commit()

        # Close communication with the database
        cursor.close()
        
        return True
