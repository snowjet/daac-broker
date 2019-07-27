@app.get("/projects")
def get_projects():

    project_list = guacoc.list_projects()

    return {"projects:", project_list}
