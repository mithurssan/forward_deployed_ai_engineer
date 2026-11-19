import logging

def configure_logging():
    logger = logging.getLogger("complaints_api")

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        "sample_logs.jsonl",
        encoding="utf-8",
    )

    file_handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    logger.addHandler(file_handler)

    return logger