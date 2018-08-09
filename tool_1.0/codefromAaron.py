import boto3
from collections import defaultdict



def listIAMusers(temp_access_storage, temp_secret_storage):
    print("check")
    temp = temp_access_storage, temp_secret_storage
    client = boto3.client('iam', aws_access_key_id=temp[0], aws_secret_access_key=temp[1])
    print("List of IAM users on your accounts: ")

    users = client.list_users()
    user_list = []
    for key in users['Users']:
        result = {}
        Policies = []
        Groups = []

        result['userName'] = key['UserName']
        list_of_policies = client.list_user_policies(UserName=key['UserName'])

        result['Policies'] = list_of_policies['PolicyNames']

        list_of_groups = client.list_groups_for_user(UserName=key['UserName'])

        for Group in list_of_groups['Groups']:
            Groups.append(Group['GroupName'])
        result['Groups'] = Groups

        list_of_mfa_devices = client.list_mfa_devices(UserName=key['UserName'])

        if not len(list_of_mfa_devices['MFADevices']):
            result['MFA Configured'] = False
        else:
            result['MFA Configured'] = True
            user_list.append(result)

    for key in user_list:
        print(key)

    #users = client.list_users()
    #for key in users['Users']:
        #print(key['UserName'])
    #for key in users['Users']:
        #list_of_policies = client.list_user_policies(UserName=key['UserName'])
        #for key in list_of_policies['PolicyNames']:
            #print(key['PolicyName'])
def paginatorfunct():
    # Create IAM client
    iam = boto3.client('iam')

    # List users with the pagination interface
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        print(response)


printWelcomeMessage()

keys = getCredentials()
# access_key = keys[0]
# secret_key = keys[1]
access_key = 'AKIAIZX2IG3B4P7BQCWA'
secret_key = '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'

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


#paginatorfunct()
file_reader_funct(access_key,secret_key)
listIAMusers(access_key, secret_key)