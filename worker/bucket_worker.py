import sys
import time

from services.bucket import conn_to_bucket, read_from_s3, save_to_s3_from_bytes
from services.redis import redis_conn, get_message_field, redis_queue_pop, update_message_status
from services.image import image_resize


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
        # print('i need resize this file', job_filename)

        # 3 retrieve from bucket
        try:
            s3 = conn_to_bucket()
            image_data = read_from_s3(s3, job_filename)
            new_filename = job_filename.split(".")[0] + "_thumb." + job_filename.split(".")[1]
        except Exception as err:
            sys.stdout.write(f"Bucket connection fail. {err}\n")
            sys.stdout.flush()
            return update_message_status(job_id, "failed")

        # 4 resize
        try:
            img_bytes = image_resize(image_data)
        except Exception as err:
            sys.stdout.write(f"Resize algorithmn fail. {err}\n")
            sys.stdout.flush()
            return update_message_status(job_id, "failed")

        # 5 store result on bucket
        try:
            save_to_s3_from_bytes(s3, img_bytes, new_filename)
        except Exception as err:
            sys.stdout.write(f"Redis connection fail. {err}\n")
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
    print("start")
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