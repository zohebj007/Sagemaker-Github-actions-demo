# deploy/deploy_pipeline.py
import boto3
import json
import os
import logging

# Make sure this imports your pipeline object
# pipeline.pipeline should create a Pipeline object and expose it as `pipeline`
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # allow import from repo root
from pipeline.pipeline import pipeline  # your pipeline.py must expose `pipeline` variable

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

SM = boto3.client("sagemaker", region_name=os.environ.get("AWS_REGION", "ap-south-1"))

PIPELINE_NAME = pipeline.name
ROLE_ARN = os.environ.get("PIPELINE_ROLE_ARN")  # CI should set this env var to the pipeline role

def upsert_pipeline():
    definition = pipeline.definition()  # JSON string of pipeline
    try:
        logger.info("Trying to create pipeline %s", PIPELINE_NAME)
        SM.create_pipeline(
            PipelineName=PIPELINE_NAME,
            PipelineDefinition=definition,
            RoleArn=ROLE_ARN
        )
        logger.info("Pipeline created")
    except Exception as e:
        logger.warning("Create failed (%s), trying update...", e)
        # Update existing pipeline
        SM.update_pipeline(
            PipelineName=PIPELINE_NAME,
            PipelineDefinition=definition
        )
        logger.info("Pipeline updated")

if __name__ == "__main__":
    upsert_pipeline()