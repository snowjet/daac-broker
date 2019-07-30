import uvicorn
from app.db.database import DataBase
from app.core.log import logger

if __name__ == "__main__":

    try:
        logger.info("Connecting to DB")

        initDB = DataBase()
        initDB.load_schmea_safe()
        initDB.disconnect()

        uvicorn.run(
            app="app.main:app", host="0.0.0.0", port=8080, log_level="info", reload=True
        )

    except Exception as error_msg:
        logger.error("Error occurred starting", error=error_msg)
