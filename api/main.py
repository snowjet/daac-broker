from fastapi import FastAPI
from pydantic import BaseModel

from guaclibs.security import generate_password
from guaclibs.db import GuacDatabaseAccess
from guaclibs.oc import GuacOpenShiftAccess
from guaclibs.log import daac_logging

log = daac_logging()
logger = log.get_logger()

guacdb = GuacDatabaseAccess()
guacoc = GuacOpenShiftAccess()

app = FastAPI()


class DCaaS_Params(BaseModel):
    password: str


@app.get("/")
def read_root():
    return {"Guac API Broker - connect to /docs for an API breakdown"}


@app.get("/users/")
def get_all_users():

    msg = guacdb.test()

    return {"users:", msg}


@app.get("/users/{username}")
def get_users(username: str):

    msg = guacdb.test()

    return {"users": msg}


@app.get("/projects")
def get_projects():

    project_list = guacoc.list_projects()

    return {"projects:", project_list}


@app.get("/services")
def get_services():

    service_list = guacoc.list_services()

    return {"services:", service_list}


@app.put("/add-user/{username}")
def add_user(username: str, dcaas_params: DCaaS_Params):

    hostname = f"desktop-{username}"
    password = dcaas_params.password

    rdp_password = generate_password()

    guacdb.add_user(username, password)
    guacdb.create_connection(username, hostname, password=rdp_password)
    guacdb.join_connection_to_user(username, hostname)

    dc_msg, svc_msg = guacoc.create_user_daac(username, rdp_password)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}
