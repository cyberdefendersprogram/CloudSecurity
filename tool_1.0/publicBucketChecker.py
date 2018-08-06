import boto3
from collections import defaultdict

access_key = '???'
secret_key = '!!!'

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

def parse_credential_file():
    credential_file = input("Do you have a AWS Credentials file Downloaded? Please provide a file name if you do: ")
    return credential_file
def getCredentials():
    credential_file = input("Do you have a AWS Credentials file Downloaded? Please provide a file name if you do: ")

        #accessKey = input("AWS Access Key ID?: ")
        #secretKey = input("AWS Secret Access Key?: ")
        #print('')
        #return [accessKey, secretKey]



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

def file_reader_funct(access_key,secret_key):
    import csv

    with open('credentials.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'\t Columns: {" || ".join(row)}')
                line_count += 1
                print(line_count)
            else:
                print(f'\n  Rows:\n \t Username: {row[0]} \n \t Password: {row[1]} \n \t Access-Key: {row[2]} '
                      f'\n \t Secret_access_key: {row[3]} \n \t Console-Link - {row[4]}.')

                # temp_user_storage = row[0], temp_pass_storage = row[1],
                temp_access_storage = row[2]
                temp_secret_storage = row[3]

                 access_key = temp_access_storage

                return [temp_access_storage, temp_secret_storage]

                line_count += 1
                print(f'Processed {line_count} lines.')


# Main Method


printWelcomeMessage()

keys = getCredentials()
# access_key = keys[0]
# secret_key = keys[1]
access_key = '???'
secret_key = '!!!'

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