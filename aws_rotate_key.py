mport boto3
from datetime import datetime, timezone
import sys

MAX_KEY_AGE=90 # This is the max age 90 days of Access Token
DEBUG = 1 # For Internal Testing only make it 1, for production always this should be 0

def age_of_key(key_creation_date):
    current_date = datetime.now(timezone.utc)
    age = (current_date - key_creation_date).days
    return age

def rotate_key(access_key):
    client = boto3.client("iam")
    paginator = client.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            username = user['UserName']
            listkey = client.list_access_keys(
                UserName=username)
            for accesskey in listkey['AccessKeyMetadata']:
                accesskey_id = accesskey['AccessKeyId']
                if access_key in accesskey_id:
                    key_creation_date = accesskey['CreateDate']
                    age = age_of_key(key_creation_date)
                    if age < MAX_KEY_AGE:
                        return "NO CHANGE"
                    else:
                        client.update_access_key(UserName="test-user-keyrotate", AccessKeyId=accesskey_id,Status='Inactive')
                        try:
                            new_key = client.create_access_key( UserName='test-user-keyrotate')
                        except IAM.Client.exceptions.LimitExceededException:
                            client.delete_access_key(UserName='test-user-keyrotate',AccessKeyId=accesskey_id)
                            new_key = client.create_access_key( UserName='test-user-keyrotate')
                else:
                    continue

    if new_key['AccessKey']:
        return new_key['AccessKey']['AccessKeyId'],new_key['AccessKey']['SecretAccessKey']
    else:
        return "ERROR"


if DEBUG:
    rotate_key('TEST_USER')
else:
    rotate_key(sys.argv[1])
