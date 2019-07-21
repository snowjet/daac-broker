import uvicorn
from guaclibs.db import GuacDatabaseAccess
from guaclibs.log import daac_logging

log = daac_logging()
logger = log.get_logger()

if __name__ == "__main__":

    try:
        logger.info("Connecting to DB")
        guacdb = GuacDatabaseAccess()
        guacdb.load_schmea_safe()
        guacdb.disconnect()

        uvicorn.run(
            app="api.main:app", host="0.0.0.0", port=8080, log_level="info", reload=True
        )

    except Exception as error_msg:
        logger.error("Error Occured starting guac-api", error=error_msg)
