import logging

def get_logger(name="processor"):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    return logging.getLogger(name)
