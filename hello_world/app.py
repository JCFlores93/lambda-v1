from __future__ import print_function
import boto3
from decimal import Decimal
import json
import urllib
import uuid
from datetime import datetime
import time
import os
import base64
from utils import ANIMALS


rekognition_client = boto3.client('rekognition')
AWS_BUCKET_NAME = 'aws-flores-test'
# import requests

def encodeImageStr(file): 
    with open(file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('ascii')
    return encoded_string

def decodeImageStr(encodedImage):
    decodedImage = base64.b64decode(encodedImage)
    return decodedImage

def encodeBytes(b):
    encodedBytes =  base64.b64encode(b)
    return encodedBytes

def detect_label(image):
    try:
        response = rekognition_client.detect_labels(Image={'Bytes': image},MaxLabels=12,
        MinConfidence=70)
        return response
    except Exception as e:
        print("Error processing detect label rekognition")
        raise e

def from_encoded_string_to_bytes(file):
    #with open(file, "rb") as cf:
    #    base64_image = base64.b64encode(cf.read())
    #    print('string')
    #    print(base64_image)

    try:
        #base_64_binary = base64.decodebytes(file)
        base_64_binary = base64.b64decode(file).decode('utf-8')
        return base_64_binary
    except Exception as e:
        print("Error processing detect label")
        raise e


def detect_allowed_animal(labels):
    labels_tested = [ label for label in labels if label.lower() in ANIMALS]
    return bool(len(labels_tested))

def save_to_bucket(timestamp,counter, bytes):
    file_name = f'{timestamp}_{counter}.jpg'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    try:
        bucket.put_object(
            ACL='public-read',
            ContentType='application/json',
            Key=file_name,
            Body=bytes,
        )
    except Exception as e:
        print(f'Error {e}')
        raise e

    return {
        "uploaded": True,
        "bucket": AWS_BUCKET_NAME,
        "path": file_name,
        "position": counter
    }
def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    #request = json.dumps(event, indent=2, skipkeys=True)
    request = json.loads(event['body'])
    images_length = request['images_length']
    pictures = request['pictures']
    print(request)
    #image = body['image']
    for pic in pictures:
        print(pic)

    #Images' length
    images_counter = 4
    #Get images from app
    response_list = []
    index = 0
    for picture in request['pictures']:
        # get binary from encoded string
        base_64_binary = from_encoded_string_to_bytes(picture)
        print('binary')
        print(base_64_binary)
        try:
            response = detect_label(base_64_binary)
            labels = [{label_prediction['Name']: label_prediction['Confidence']} for label_prediction in
                      response['Labels']]
            keys = [list(label.keys())[0] for label in labels]
            values = [list(label)[0] for label in labels]
            allowed_picture = detect_allowed_animal(values)
            if allowed_picture:
                timestamp = datetime.now().timestamp()
                saved_object = save_to_bucket(timestamp, index, base_64_binary)
                if saved_object['uploaded']:
                    response_list.append(saved_object)
                else:
                    body = {
                        "uploaded": False,
                        "path": '',
                        "position": index,
                    }
                    response_list.append(body)
            else:
                body = {
                    "uploaded": False,
                    "path": '',
                    "position": index,
                }
                response_list.append(body)

        except Exception as e:
            print("Error")
            raise e
        index += 1
    return {
        "statusCode": 200,
        "body": json.dumps({
            'list': response_list})
    }

