# lambda/trigger_stepfunction.py
import os
import json
import boto3
import logging
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SFN = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]  # set in Lambda env

def extract_s3_path(record):
    bucket = record["s3"]["bucket"]["name"]
    key = unquote_plus(record["s3"]["object"]["key"])
    return f"s3://{bucket}/{key}"

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    records = event.get("Records", [])
    started = []
    for rec in records:
        try:
            s3_path = extract_s3_path(rec)
            # Optionally filter: only trigger on files like .csv or on a READY file
            if not s3_path.lower().endswith(".csv") and not s3_path.endswith("_READY"):
                logger.info("Ignoring key: %s", s3_path)
                continue
            payload = {"dataset_s3_path": s3_path}
            resp = SFN.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                input=json.dumps(payload)
            )
            logger.info("Started state machine execution: %s", resp.get("executionArn"))
            started.append(resp.get("executionArn"))
        except Exception as e:
            logger.exception("Failed to start execution for record: %s", e)
    return {"started_executions": started}