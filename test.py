#!/usr/bin/env python

from guaclibs.db import GuacDatabaseAccess
from guaclibs.oc import GuacOC


def main():
    print("Starting Guacamole Test")

    # myoc = GuacOC()
    # project_list = myoc.oc_connection()
    # print(project_list)

    guacdb = GuacDatabaseAccess()
    msg = guacdb.test()
    print(msg)

    guacdb.load_schmea_safe()
    guacdb.disconnect()

    # guacdb = GuacDatabaseAccess()

    # guacdb.create_connection(hostname='desktop', username='user', password='KL3ECRd9dd68xFsZ')

    # guacdb.add_user(username='user3', password='password')

    # guacdb.join_connection_to_user(username='user3', hostname='desktop')

    # guacdb.disconnect()


if __name__ == "__main__":
    main()
