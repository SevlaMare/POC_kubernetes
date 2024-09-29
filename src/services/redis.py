import os
import redis
import time
import uuid


REDIS_HOST = os.getenv(key='REDIS_HOST', default="localhost")
REDIS_PORT = os.getenv(key='REDIS_PORT', default=6379)
REDIS_DB_NUMBER = os.getenv(key='REDIS_DB_NUMBER', default=0)
REDIS_PASSWORD = os.getenv(key='REDISPASSWORD', default="secret")


def redis_conn():
    try:
      db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB_NUMBER,
        password=REDIS_PASSWORD,
        decode_responses=True
      )
      db.ping() # to force expection if no connection
    except Exception as err:
        raise Exception(f"Failed to connect to Redis: {err}") from err
    return db


# hashmap methods ---------
def add_message_to_queue(message):
    r = redis_conn()
    message_id = str(uuid.uuid4())
    r.hset(f"message:{message_id}", "status", "pending")
    r.hset(f"message:{message_id}", "timestamp", int(time.time()))
    r.hset(f"message:{message_id}", "filename", str(message))
    return message_id


def get_message_status(message_id):
    r = redis_conn()
    status = r.hget(f"message:{message_id}", "status")
    return status


def get_message_field(message_id, field = "filename"):
    r = redis_conn()
    field = r.hget(f"message:{message_id}", field)
    return field


def update_message_status(message_id, status):
    r = redis_conn()
    r.hset(f"message:{message_id}", "status", status)
    r.hset(f"message:{message_id}", "timestamp", int(time.time()))


def get_messages():
    r = redis_conn()
    message_keys = r.keys("message:*")
    return message_keys


# FIFO queue methods ---------
def redis_queue_push(conn, job_id, redis_queue_name = "jobs"):
    """FIFO queue push"""
    conn.lpush(redis_queue_name, job_id)


def redis_queue_pop(conn, redis_queue_name = "jobs"):
    """FIFO queue pop"""
    # `b` indicates this is a blocking call
    # waits until an item becomes available.
    _, message_json = conn.brpop(redis_queue_name)
    return message_json
