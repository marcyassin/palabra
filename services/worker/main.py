from worker.tasks.process_book import process_book
from worker.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Processor started.")
    process_book(1, "00bfe969-ec54-469b-a581-a4969c147886-cixin.epub")

if __name__ == "__main__":
    main()
