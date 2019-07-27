

@app.put("/admin/add-user/{username}")
def add_user(username: str, dcaas_params: DCaaS_Params):

    hostname = f"desktop-{username}"
    password = dcaas_params.password

    rdp_password = generate_password()
    password_hash = hash_password(password=rdp_password)

    guacdb.confirm_db_connection()
    guacdb.add_user(username, password)
    guacdb.create_connection(username, hostname, password=rdp_password)
    guacdb.join_connection_to_user(username, hostname)

    dc_msg, svc_msg = guacoc.create_user_daac(username, password_hash)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}

# Admin Functions
@app.put("/admin/prepare-db")
def prepare_db():

    guacdb.confirm_db_connection()
    msg = guacdb.load_schmea_safe()

    return {"prepare-db": msg}