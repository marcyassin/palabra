from processor.tasks.process_book import process_book
from processor.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Processor started.")
    # process_book(1, "f95b9737-fb6a-4feb-ba0c-07cf21732299-cixin.epub")
    process_book(1, "f95b9737-fb6a-4feb-ba0c-07cf21732299-cixin.epub")

if __name__ == "__main__":
    main()
