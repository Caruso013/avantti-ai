import time
import os
import json
import asyncio
from utils.logger import logger, to_json_dump
from dotenv import load_dotenv
from exceptions.handler import handle_errors, setup_error_handler

load_dotenv()
from container.container import Container

DEBOUNCE_SECONDS = os.getenv("DEBOUNCE_SECONDS", 5)
QUEUE_KEY = os.getenv("QUEUE_KEY", "message_queue")

container = Container()
setup_error_handler(container)
redis = container.clients.cache


@handle_errors("QUEUE_WORKER")
async def run_queue_worker():
    logger.info(
        f'[QUEUE WORKER] Starting in the queue "{QUEUE_KEY}" with debounce {DEBOUNCE_SECONDS} seconds.'
    )

    while True:
        try:
            now = int(time.time())
            queue = redis.get_queue(QUEUE_KEY)
            keys_to_delete = []

            for phone, raw_data in queue.items():
                data = json.loads(raw_data)

                if data["expired_at"] > now:
                    continue

                asyncio.create_task(
                    container.services.generate_response_service.execute(
                        phone=phone, message=data["value"]
                    )
                )

                keys_to_delete.append(phone)

            if keys_to_delete:
                redis.delete_queue(QUEUE_KEY, keys_to_delete)

        except Exception as e:
            logger.exception(
                f"[QUEUE WORKER] ❌ Erro ao executar o queue worker: \n{to_json_dump(e)}"
            )
            raise e

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_queue_worker())
