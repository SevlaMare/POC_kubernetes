import os
import sys
import time
from PIL import Image

from services.redis import redis_conn, get_message_field, redis_queue_pop, update_message_status
from services.upload import IMAGEDIR


def main():
    try:
        db = redis_conn()
        job_id = redis_queue_pop(db) # picked from queue
    except Exception as err:
        sys.stdout.write(f"Bucket connection fail. {err}\n")
        sys.stdout.flush()
        return update_message_status(job_id, "failed")

    try:
        # 1 signal that processing has started
        update_message_status(job_id, "processing")

        # 2 get metadata
        job_filename = get_message_field(job_id, "filename")

        # 3 retrieve and resize
        try:
            path = str(IMAGEDIR / job_filename)
            path = path.replace("worker", "src")
            new_filename = "thumb_" + job_filename

            img = Image.open(path)
            img_resized = img.resize((100, 100), resample=Image.NEAREST)

            new_path = os.path.join(os.path.dirname(path), new_filename)
            img_resized.save(new_path)

            sys.stdout.write(f"store info. {new_path}\n")
            sys.stdout.flush()

        except Exception as err:
            sys.stdout.write(f"Resize algorithmn fail. {err}\n")
            sys.stdout.flush()
            return update_message_status(job_id, "failed")

        update_message_status(job_id, "succeeded")

    except Exception as err:
        # 5 if fail, sinal
        sys.stdout.write(f"Error processing message:... {err}\n")
        sys.stdout.flush()
        return update_message_status(job_id, "failed")

    return job_id


if __name__ == "__main__":
    sys.stdout.write("starting worker.\n")
    sys.stdout.flush()
    working = True
    try:
        while working:
            main()
            time.sleep(1)
    except KeyboardInterrupt:
        working = False
        sys.stdout.write("Worker stopped.\n")
        sys.stdout.flush()
    except Exception as err:
        sys.stdout.write(f"Error while running worker: {err}\n")
        sys.stdout.flush()
    sys.stdout.write("worker shutdown...")
    sys.stdout.flush()