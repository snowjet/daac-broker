from fastapi import FastAPI
from pydantic import BaseModel

from guaclibs.db import GuacDatabaseAccess
from guaclibs.oc import GuacOC

app = FastAPI()


class DCaaS_Params(BaseModel):
    password: str

@app.get("/")
def read_root():
    return {"Guac API Broker - connect to /docs for an API breakdown"}


@app.get("/users/")
def get_all_users():

    guacdb = GuacDatabaseAccess()
    msg = guacdb.test()

    return {"users:", msg}


@app.get("/users/{username}")
def get_users(username: str):

    guacdb = GuacDatabaseAccess()
    msg = guacdb.test()

    return {"users": msg}


@app.get("/projects")
def get_projects():

    myoc = GuacOC()
    project_list = myoc.list_projects()

    return {"projects:", project_list}


@app.get("/services")
def get_services():

    myoc = GuacOC()
    service_list = myoc.list_services()

    return {"services:", service_list}

@app.put("/add-user/{username}"
def add_user(username: str, dcaas_params: DCaaS_Params):

    guacdb = GuacDatabaseAccess()
    myoc = GuacOC()

    return {"user-added": username}
