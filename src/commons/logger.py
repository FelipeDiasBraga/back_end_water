from loguru import logger
from commons import config
import psutil
import json
import os
from datetime import datetime
import sys


def serialize(record):
    log = {
        "timestamp": f"""{record['time'].strftime("%Y-%m-%d %H:%M:%S")}""",
        "level": f"{record['level']}",
        "component_service_name": f"PLACEHOLDER",
        "event": f"PLACEHOLDER",
        "message": f"{record['message']}",
        "context": f"PLACEHOLDER",
        "resource_name": f"{os.environ.get('HOSTNAME') or os.environ.get('COMPUTERNAME')}",
        "deployment_id": f"PLACEHOLDER",
        "environment": f"PLACEHOLDER",
        "step_execution_time": f"{record['elapsed']}",
        "automation_phase": "POST DEPLOYMENT",
        "RAM_usage": f"{psutil.virtual_memory().percent}",
        "CPU_usage": f"{psutil.cpu_percent(interval=1)}",
        "tenant": "PLACEHOLDER",
    }

    return json.dumps(log)


def formatter(record):
    # Note this function returns the string to be formatted, not the actual message to be logged
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"


logger.remove()
# logger.add(
#     os.path.join(
#         config.LOG_FOLDER,
#         f"""{datetime.strftime(datetime.now(),"%m-%d-%Y-%H-%M-%S")}.json""",
#     ),
#     format=formatter,
# )
logger.add(
    os.path.join(
        config.LOG_FOLDER,
        f"""{datetime.strftime(datetime.now(),"%m-%d-%Y-%H-%M-%S")}.log""",
    ),
    rotation="1 day",
)
logger.add(sys.stdout, colorize=True)
logger.info("Logging to file")
