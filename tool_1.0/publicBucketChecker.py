import boto3
# import os
# import re
# import sys
# import warnings
#
# from datetime import datetime, timedelta
# from os.path import expanduser
from collections import defaultdict

access_key = 'AKIAIK3TIWAEPAKQIZMA'
secret_key = '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'
report_path = "/tmp/report.txt"

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}
numBuckets = 0
numPublicBuckets = 0


def printWelcomeMessage():
    msg = 'Welcome to the Snow Cloud Program!' + '\n'
    print(msg)


def printNumBuckets():
    msg = 'The TOTAL number of buckets is: ' + str(numBuckets)
    print(msg)

def printNumPublicBuckets():
    msg = 'The TOTAL number of PUBLIC buckets is: ' + str(numPublicBuckets)
    print(msg)

def add_to_output(msg):
    print(msg)


def get_location(bucket_name, s3_client):
    """
    Returns the bucket location.
    :param bucket_name: Name of the bucket.
    :param s3_client: s3_client instance.
    :return: String with bucket's region.
    """
    loc = s3_client.get_bucket_location(
            Bucket=bucket_name)["LocationConstraint"]
    if loc is None:
        loc = "None(probably Northern Virginia)"
    return loc


def check_acl(acl):
    """
    Checks if the Access Control List is public.
    :param acl: Acl instance that describes bucket's.
    :return: Bucket's public indicator and dangerous grants parsed from acl instance.
    """
    dangerous_grants = defaultdict(list)
    for grant in acl.grants:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group" and grantee["URI"] in GROUPS_TO_CHECK:
            dangerous_grants[grantee["URI"]].append(grant["Permission"])
    public_indicator = True if dangerous_grants else False
    return public_indicator, dangerous_grants


def getCredentials():
    accessKey = input("AWS Access Key ID?: ")
    secretKey = input("AWS Secret Access Key?: ")
    print('')
    return [accessKey, secretKey]

# Main Method

printWelcomeMessage()

keys = getCredentials()
access_key = keys[0]
secret_key = keys[1]

s3 = boto3.resource("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
s3_client = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)

buckets = s3.buckets.all()
msg = ''

for bucket in buckets:
    location = get_location(bucket.name, s3_client)
    # add_to_output(report_path)
    bucket_acl = bucket.Acl()
    public, grants = check_acl(bucket_acl)
    numBuckets += 1


    if public:
        if report_path:
            msg = "Bucket {}: {}".format(bucket.name, "PUBLIC! VERY BAD! :(")
            numPublicBuckets += 1
    else:
        if report_path:
            msg = "Bucket {}: {}".format(bucket.name, "NOT PUBLIC! Good!")
    print(msg)
    print("Location: {}".format(location))
    print('')

printNumBuckets()
printNumPublicBuckets()
