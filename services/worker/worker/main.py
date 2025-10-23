"""
Main RQ worker entrypoint.
Listens to Redis queues and executes background jobs with graceful shutdown.
"""

import signal
import sys
import redis
from rq import Worker
from worker.config.settings import REDIS_URL

# Import tasks so RQ knows them
from worker.tasks import process_book  # noqa: F401

# Global flag to handle stop signals
should_stop = False


def handle_signal(signum, frame):
    """Catch SIGTERM/SIGINT to allow graceful shutdown."""
    global should_stop
    print(f"\n🛑 Received signal {signum}. Stopping after current job...")
    should_stop = True


def main():
    print("🚀 Starting Palabra RQ Worker...")

    # Handle signals gracefully
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Connect to Redis
    redis_conn = redis.from_url(REDIS_URL)

    # Define which queues this worker should process
    queues = ["books"]

    worker = Worker(queues=queues, connection=redis_conn)
    print(f"🎧 Listening on queues: {queues}")

    try:
        while not should_stop:
            # Work continuously, checking signals each loop
            worker.work(
                burst=False,          # keep listening for jobs
                with_scheduler=True,  # allow delayed jobs
                max_jobs=1000         # optional safety cap
            )
    except Exception as e:
        print(f"💥 Worker error: {e}")
    finally:
        print("👋 Worker shutting down cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
