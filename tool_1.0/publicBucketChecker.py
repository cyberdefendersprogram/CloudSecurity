import boto3
import time
import csv
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

            print('Last active date:    ', end='')
            print(last_activity.date())
            days = datetime.datetime.now().date() - last_activity.date()
            print('Inactive for:        ', end='')
            print(days)


def root_keys_active(credreport, index):
    if (credreport[index]['access_key_1_active'] == 'true') or (credreport[index]['access_key_2_active'] == 'true'):
        return True
    else:
        return False


def get_cred_report():
    x = 0
    try:
        while iam_client.generate_credential_report()['State'] != "COMPLETE":
            time.sleep(2)
            x += 1
            # If no credential report is delivered within this time fail the check.
            if x > 10:
                return "Fail: rootUse - no CredentialReport available."

        response = iam_client.get_credential_report()

        report = []
        reportText = response['Content'].decode("utf-8").splitlines()
        if not reportText:
            print('Failed')
            return "Fail: Report is empty"
        reader = csv.DictReader(reportText, delimiter=',')
        for row in reader:
            report.append(row)
            # Verify if root key's never been used, if so add N/A
        try:
            if report[0]['access_key_1_last_used_date']:
                pass
        except:
            report[0]['access_key_1_last_used_date'] = "N/A"
        try:
            if report[0]['access_key_2_last_used_date']:
                pass
        except:
            report[0]['access_key_2_last_used_date'] = "N/A"
        return report

    except Exception as e:
        return "Fail: Error retrieving data "+str(e)

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

iam_client = boto3.client("iam", aws_access_key_id=access_key, aws_secret_access_key=secret_key)

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
print('')

################################# IAM ###################################

print('IAM Report ----------------------------------------------------- \n')

cred_report = get_cred_report()

num_users = cred_report.__len__()
print('The number of Users (Including the Root User) is: ',end='')
print(str(num_users) + '\n')

for i in range(0, num_users):
    # User Name and Whether or not the Key is active
    print('User' + str(i + 1) + ':       ', end='')

    print(cred_report[i]['user'])

    print('             Access Key Active?:     ', end='')
    if root_keys_active(cred_report, i):
        print('Active!')
    else:
        print('NOT Active.')

    # Access Key Last used date

    # Creation Date
    creationTime = cred_report[i]['user_creation_time']
    print('             User Creation Date:     ' + creationTime[:10])

    # Password last used
    passwordLastUsed = cred_report[i]['password_last_used']
    print('             Password Last Used:     ' + passwordLastUsed[:10], end='')
    if passwordLastUsed[9:10] == 'a':
        print('tion')
    else:
        print('')
    # mfa Active
    print('             MFA Active:             ' + cred_report[i]['mfa_active'])
    print('')

if root_keys_active(cred_report, 0):
    print('Root Access Keys Active ! ! !')
else:
    print('No Root Access Keys.')
