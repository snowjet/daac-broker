

@app.get("/services")
def get_services():

    service_list = guacoc.list_services()

    return {"services:", service_list}