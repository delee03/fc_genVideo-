import json
import boto3
import random
import time

AWS_REGION = "us-east-1"
MODEL_ID = "amazon.nova-reel-v1:0"
SLEEP_TIME = 30
S3_DESTINATION_BUCKET = "reelvideoshutech"

video_prompt = "An adventurous movie scene, an explorer in a jungle discovering an ancient temple covered in vines, sunlight breaking through the canopy, cinematic composition, ultra-detailed, 4k, realistic textures, mysterious and exciting mood."

bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)
model_input = {
    "taskType": "TEXT_VIDEO",
    "textToVideoParams": {"text": video_prompt},
    "videoGenerationConfig": {
        "durationSeconds": 6,
        "fps": 24,
        "dimension": "1280x720",
        "seed": random.randint(0, 2147483648)
    }
}

invocation = bedrock_runtime.start_async_invoke(
    modelId=MODEL_ID,
    modelInput=model_input,
    outputDataConfig={"s3OutputDataConfig": {"s3Uri": f"s3://{S3_DESTINATION_BUCKET}"}}
)

invocation_arn = invocation["invocationArn"]
s3_prefix = invocation_arn.split('/')[-1]
s3_location = f"s3://{S3_DESTINATION_BUCKET}/{s3_prefix}"
print(f"\nS3 URI: {s3_location}")

while True:
    response = bedrock_runtime.get_async_invoke(
        invocationArn=invocation_arn
    )
    status = response["status"]
    print(f"Status: {status}")
    if status != "InProgress":
        break
    time.sleep(SLEEP_TIME)

if status == "Completed":
    print(f"\nVideo is ready at {s3_location}/output.mp4")
else:
    print(f"\nVideo generation status: {status}")