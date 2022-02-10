import boto3
from datetime import datetime, timezone

MAX_KEY_AGE=5
DEBUG = 1

def age_of_key(key_creation_date):
    current_date = datetime.now(timezone.utc)
    age = (current_date - key_creation_date).days
    return age

def rotate_key():
    client = boto3.client("iam")
    paginator = client.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            username = user['UserName']
            listkey = client.list_access_keys(
                UserName=username)
            for accesskey in listkey['AccessKeyMetadata']:
                accesskey_id = accesskey['AccessKeyId']
                key_creation_date = accesskey['CreateDate']
                age = age_of_key(key_creation_date)
                if DEBUG:
                    print("This is for Testing ")
                    client.update_access_key(UserName="test-user-keyrotate", AccessKeyId=accesskey_id, Status='Inactive')
                    print("Succesfully Rotated Key For : test-user-keyrotate")
                    return True
                if age > MAX_KEY_AGE:
                    print("Deactivating Key for the following users: " + username)
                    client.update_access_key(UserName=username, AccessKeyId=accesskey_id, Status='Inactive')
                    print(f"Succesfully Key Rotated for {username}")
rotate_key()
