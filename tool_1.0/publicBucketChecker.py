import boto3
import datetime
from collections import defaultdict


##################[ METHODS ]##################

def printWelcomeMessage():
    msg = '\n' + '|*||*||*||*||*| Welcome to the Snow Cloud S3 Bucket Checker |*||*||*||*||*|' + '\n'
    return msg


def printNumBuckets():
    msg = 'The total number of buckets:         ' + str(numBuckets)
    return msg


def printNumPublicBuckets():
    # @!!!!! maybe can can add a message why they need to be carefule with public bucket
    msg = 'The total number of PUBLIC buckets:  ' + str(numPublicBuckets) + '\n'
    return msg


def getCredentials():
    accessKey = input("AWS Access Key ID?: ")
    secretKey = input("AWS Secret Access Key?: ")
    return [accessKey, secretKey]


def get_location(bucket_name, s3_client):
    """
    Returns the bucket location.
    - INPUT: bucket_name: Name of the bucket, s3_client: s3_client instance.
    - OUTPUT: loc(str): a bucket's region
    """
    loc = s3_client.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]

    if loc is None:
        loc = "NONE"

    return loc


def check_acl(acl):
    """
    Checks if the Access Control List is public.
    - INPUT: Acl instance
    - OUTPUT: is_public(boolean): public or not,
    """
    dangerous_grants = defaultdict(list)

    for grant in acl.grants:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group" and grantee["URI"] in GROUPS_TO_CHECK:
            dangerous_grants[grantee["URI"]].append(grant["Permission"])

    is_public = True if dangerous_grants else False

    return is_public

def s3_last_used(s3_client, bucket_name):
    last_activity = 'N/A'
    object_list = s3_client.list_objects_v2(Bucket=bucket_name, FetchOwner=True)
    if 'Contents' in object_list:
        for object in object_list['Contents']:
            if last_activity == 'N/A' or last_activity > object['LastModified']:
                last_activity = object['LastModified']
        if last_activity.date() < datetime.datetime.now().date():
            print('Bucket Name:         ' + bucket_name)
            print('Last active date:    ', end='')
            print(last_activity.date())
            days = datetime.datetime.now().date() - last_activity.date()
            print('Inactive for:        ', end='')
            print(days)


##################[ MAIN ]##################

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

numBuckets = 0
numPublicBuckets = 0
msg = ''

# Start with welcome message
print(printWelcomeMessage())

# Get credentials to access s3 account
keys = getCredentials()
print('\n' + '–––––––––––––––– Scannning.... ––––––––––––––––' + '\n')
access_key = keys[0]
secret_key = keys[1]

# Define S3 as the AWS service that we are goign to use
s3 = boto3.resource("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
# Provide credentials to boto3
s3_client = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Get all s3 buckets
buckets = s3.buckets.all()

# Get info of each bucket
for bucket in buckets:
    location = get_location(bucket.name, s3_client)
    # add_to_output(report_path)
    bucket_acl = bucket.Acl()
    public = check_acl(bucket_acl)
    numBuckets += 1

    msg = "Bucket:              {}".format(bucket.name)
    print(msg)

    if public:
        print('Security:            PUBLIC ! ! ! UNSECURE ! ! !')
        numPublicBuckets += 1
    else:
        print('Security:            private :)')

    print("Location:            {}".format(location))
    s3_last_used(s3_client, bucket.name)
    print('')

print(printNumBuckets())
print(printNumPublicBuckets())
