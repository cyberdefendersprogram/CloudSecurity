import boto3
from collections import defaultdict
import time
import datetime


##################[ METHODS ]##################


def printNumBuckets(): 
    msg = 'The total number of buckets: ' + str(numBuckets)
    return msg


def printNumPublicBuckets():
    # @!!!!! maybe can can add a message why they need to be carefule with public bucket 
    msg = 'The total number of PUBLIC buckets: ' + str(numPublicBuckets) + '\n'
    return msg


def get_location(bucket_name, s3_client):
    """
    Returns the bucket location.
    - INPUT: bucket_name: Name of the bucket, s3_client: s3_client instance.
    - OUTPUT: loc(str): a bucket's region
    """
    loc = s3_client.get_bucket_location(Bucket = bucket_name)["LocationConstraint"]
    
    if loc is None:
        loc = "NONE"
    
    return loc


def check_acl(acl, group):
    """
    Checks if the Access Control List is public.
    - INPUT: Acl instance
    - OUTPUT: is_public(boolean): public or not, 
    """
    dangerous_grants = defaultdict(list)
    
    for grant in acl.grants:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group" and grantee["URI"] in group:
            dangerous_grants[grantee["URI"]].append(grant["Permission"])
    
    is_public = True if dangerous_grants else False 
    
    return is_public


# Prints the last activity date and how many days the the s3 bucket has been inactive for
# Input: s3_client: s3 instance, bucket_name: name of s3 bucket in AWS
def s3_last_used(s3_client, bucket_name):
    last_activity = 'N/A'
    object_list = s3_client.list_objects_v2(Bucket=bucket_name, FetchOwner=True)
    if 'Contents' in object_list:
        for object in object_list['Contents']:
            if last_activity == 'N/A' or last_activity > object['LastModified']:
                last_activity = object['LastModified']
        if last_activity.date() < datetime.datetime.now().date():
            print('Last active date:    ', end='')
            print(str(last_activity.date()))
            days = datetime.datetime.now().date() - last_activity.date()
            print('Inactive for:        ', end='')
            days_str = str(days)
            if days_str[5:6] == 's':
                days_str = days_str[:6]
            else:
                days_str = days_str[:7]
            print(str(days_str))
            print('')


def main(s3, client, group):
    numBuckets = 0
    numPublicBuckets = 0

    # Get all s3 buckets 
    buckets = s3.buckets.all()

    # Get info of each bucket
    for bucket in buckets:
        # get location of bucket 
        location = get_location(bucket.name, client)
        # retrieve the policy grant info
        bucket_acl = bucket.Acl()
        public = check_acl(bucket_acl, group)
        numBuckets += 1

        # render message
        msg = "Bucket:              {}".format(bucket.name)
        print(msg)

        if public:
            print('Security:            PUBLIC ! ! ! UNSECURE ! ! !')
            numPublicBuckets += 1
        else:
            print('Security:            private :)')
        print("Location:            {}".format(location))

        s3_last_used(client, bucket.name)

    print('The total number of PUBLIC buckets:  ', numPublicBuckets)
    print('The total number of buckets:         ', numBuckets)
