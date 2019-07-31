import uvicorn

from core.log import logger
from db.db_utils import load_schema_safe

if __name__ == "__main__":

    try:
        logger.info("Connecting to DB")

        msg = load_schema_safe()
        logger.info("Load Schema", output=msg)

        uvicorn.run(
            app="main:app", host="0.0.0.0", port=8080, log_level="info", reload=True
        )

    except Exception as error_msg:
        logger.error("Error occurred starting", error=error_msg)
