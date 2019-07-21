import uvicorn
from guaclibs.db import GuacDatabaseAccess

if __name__ == "__main__":

    guacdb = GuacDatabaseAccess()
    guacdb.load_schmea_safe()
    guacdb.disconnect()

    uvicorn.run(
        app="api.main:app", host="0.0.0.0", port=8080, log_level="info", reload=True
    )
