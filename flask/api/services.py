@router.get("/services")
def get_services():

    service_list = guac.list_services()

    return {"services:", service_list}
