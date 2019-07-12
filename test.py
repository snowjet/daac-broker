#!/usr/bin/env python

from guac_libs.guac_db import GuacDatabaseAccess

def main():
    print("Starting Guacamole Broker")

    guacdb = GuacDatabaseAccess()
    
    msg = guacdb.test()
    print(msg)

    # guacdb = GuacDatabaseAccess()

    # guacdb.create_connection(hostname='desktop', username='user', password='KL3ECRd9dd68xFsZ')

    # guacdb.add_user(username='user3', password='password')

    # guacdb.join_connection_to_user(username='user3', hostname='desktop')

    # guacdb.disconnect()

if __name__ == '__main__':
    main()