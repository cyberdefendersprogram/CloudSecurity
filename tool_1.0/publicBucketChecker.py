import boto3
from collections import defaultdict


##################[ METHODS ]##################

def printWelcomeMessage():
    msg = '\n' + '|*||*||*||*||*| Welcome to the Snow Cloud S3 Bucket Checker |*||*||*||*||*|' + '\n'
    return msg


def printNumBuckets(): 
    msg = 'The total number of buckets: ' + str(numBuckets)
    return msg


def printNumPublicBuckets():
	# @!!!!! maybe can can add a message why they need to be carefule with public bucket 
    msg = 'The total number of PUBLIC buckets: ' + str(numPublicBuckets) + '\n'
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
    loc = s3_client.get_bucket_location(Bucket = bucket_name)["LocationConstraint"]
    
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


##################[ MAIN ]##################

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

numBuckets = 0
numPublicBuckets = 0

# Start with welcome message 
print(printWelcomeMessage())

# Get credentials to access s3 account
keys = getCredentials()
print('\n' + '–––––––––––––––– Scannning.... ––––––––––––––––' + '\n')
access_key = keys[0]
secret_key = keys[1]

# Define S3 as the AWS service that we are goign to use
s3 = boto3.resource("s3", aws_access_key_id = access_key, aws_secret_access_key = secret_key)
# Provide credentials to boto3
s3_client = boto3.client("s3", aws_access_key_id = access_key, aws_secret_access_key = secret_key)

# Get all s3 buckets 
buckets = s3.buckets.all()

# Get info of each bucket
for bucket in buckets:
    # get location of bucket 
    location = get_location(bucket.name, s3_client)
    # retrieve the policy grant info
    bucket_acl = bucket.Acl()
    public = check_acl(bucket_acl)
    numBuckets += 1

    # render message
    if public:
        msg = "Bucket {}: {}".format(bucket.name, "PUBLIC! VERY BAD! :(")
        numPublicBuckets += 1
    else:
        msg = "Bucket {}: {}".format(bucket.name, "NOT PUBLIC! Good!")
    print(msg)
    print("Location: {} \n".format(location))


print(printNumBuckets())
print(printNumPublicBuckets())
