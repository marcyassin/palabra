from worker.tasks.process_book import process_book
from worker.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Processor started.")
    process_book(1, "bb9c5faf-5dc1-41ca-84f1-4fa789797ff3-cixin.epub")

if __name__ == "__main__":
    main()
