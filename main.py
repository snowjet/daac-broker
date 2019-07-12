from fastapi import FastAPI
from pydantic import BaseModel
from guaclibs.db import GuacDatabaseAccess
from guaclibs.oc import GuacOC

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

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

@app.get("/projects/")
def get_project():

    myoc = GuacOC()
    project_list = myoc.oc_connection()

    return {"projects:", project_list}