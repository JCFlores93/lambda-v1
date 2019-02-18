from __future__ import print_function
import boto3
from decimal import Decimal
import json
import urllib
import uuid
import datetime
import time
import os
import base64

rekognition_client = boto3.client('rekognition')
# import requests

def detect_label(image):
    try:
        response = rekognition_client.detect_labels(Image={'Bytes': image},MaxLabels=12,
        MinConfidence=70)
        return response
    except Exception as e:
        print("Error processing detect label")
        raise e

def from_encoded_string_to_file(encoded_string):
    try:
        decoded_image = base64.b64decode(encoded_string).decode("utf-8", "ignore")
        return decoded_image
    except Exception as e:
        print("Error processing image")
        raise e

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
    body = json.loads(event['body'])
    #image = body['image']
    print(body)
    print(body['image'])

    #image = open('cat1.jpeg', 'rb')
    #image_read = image.read()
    #image_64_encode = base64.encodestring(image_read)

    #image_64_decode = base64.decodestring(image_64_encode)

    with open('cat1.jpeg', "rb") as cf:
        base64_image = base64.b64encode(cf.read())
        base_64_binary = base64.decodebytes(base64_image)

    #image_result = open('deer_decode.gif', 'wb')
    #image_result.write(image_64_decode)
    #print("Received event: " + request['body'])
    try:
        #response1 = from_encoded_string_to_file(base_64_binary)
        #print(response1)
        response = detect_label(base_64_binary)
        labels = [{label_prediction['Name']: Decimal(str(label_prediction['Confidence']))} for label_prediction in
              response['Labels']]
        keys = [ list(label.keys())[0] for label in labels]
        values = [ list(label)[0] for label in labels]
        print(keys)
            #key= list(label.keys())[0]
            #print(type(key))
            #print(key)
            #print(label[key])
            #print(label.values()[0])
            #print(value)
        # Get the timestamp.
        print(labels)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Success"
                # "location": ip.text.replace("\n", "")
            })
        }
    except Exception as e:
        print("Error")
        #print("Error processing object {} from bucket {}. Event {}".format(key, bucket, json.dumps(event, indent=2)))
        raise e

