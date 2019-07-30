import uvicorn
from app.db.db_utils import get_database_connection
from app.core.log import logger

if __name__ == "__main__":

    try:
        logger.info("Connecting to DB")

        db_conn = get_database_connection()
        db_conn.load_schmea_safe()

        uvicorn.run(
            app="app.main:app", host="0.0.0.0", port=8080, log_level="info", reload=True
        )

    except Exception as error_msg:
        logger.error("Error occurred starting", error=error_msg)
