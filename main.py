from fastapi import FastAPI
from pydantic import BaseModel
from guaclibs.db import GuacDatabaseAccess
from guaclibs.oc import GuacOC

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/users/")
def get_all_users():

    guacdb = GuacDatabaseAccess()
    msg = guacdb.test()

    return {"users:", msg}


@app.get("/users/{username}")
def get_users():

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