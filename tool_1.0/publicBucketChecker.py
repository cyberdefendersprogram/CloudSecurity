import boto3
import time
import csv
import datetime
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Prints to the console and writes to the file
# Input: msg_to_print: (str) message, line_down (boolean) if you need to print a carriage return
def printAndWrite(msg_to_print, line_down):
    print(msg_to_print, end='')
    f.write(msg_to_print)
    if line_down:
        print('')
        f.write('\n')


# Returns welcome message at the very beginning
def printWelcomeMessage():
    msg = '\n' + '|*||*||*||*||*| Welcome to the Snow Cloud AWS Checker |*||*||*||*||*|' + '\n'
    return msg

# Returns Thank You message
def thankYouMessage():
    return 'Thank you for using our snow white program!'


# Returns the total number of bucket message
def printNumBuckets():
    msg = 'The total number of buckets:         ' + str(numBuckets)
    return msg


# Returns the number of public buckets message
def printNumPublicBuckets():
    # @!!!!! maybe can can add a message why they need to be carefule with public bucket
    msg = 'The total number of PUBLIC buckets:  ' + str(numPublicBuckets) + '\n'
    return msg


# Requests the user for AWS Access Key and Secret Key
# Returns Access Key and Secret Key in array
def getCredentials():
    accessKey = input("AWS Access Key ID?: ")
    secretKey = input("AWS Secret Access Key?: ")
    return [accessKey, secretKey]


# Input: bucket_name: Name of bucket, s3_client: s3_client instance
# Returns the bucket location
def get_location(bucket_name, s3_client):
    loc = s3_client.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
    if loc is None:
        loc = "NONE"
    return loc


# Checks if the Access Control List is public.
# Input: Acl instance
# Returns boolean if public or not
def check_acl(acl):
    dangerous_grants = defaultdict(list)

    for grant in acl.grants:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group" and grantee["URI"] in GROUPS_TO_CHECK:
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
            printAndWrite('Last active date:    ', False)
            printAndWrite(str(last_activity.date()), True)
            days = datetime.datetime.now().date() - last_activity.date()
            printAndWrite('Inactive for:        ', False)
            days_str = str(days)
            if days_str[5:6] == 's':
                days_str = days_str[:6]
            else:
                days_str = days_str[:7]
            printAndWrite(str(days_str), True)


# Looks between either access key and sees if either or them are activated
# Input: credreport: credit report, index: the index within the credit report
# Return: True or False. True if active. False if inactive
def root_keys_active(credreport, index):
    if (credreport[index]['access_key_1_active'] == 'true') or (credreport[index]['access_key_2_active'] == 'true'):
        return True
    else:
        return False


# Generates and retrieves a credit report from AWS
# Return: report as dictionary item
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
            printAndWrite('Failed', True)
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


# Initial information for email setup
host = "smtp.gmail.com"
port = 587
username = "cloudreport.sw@gmail.com"
password = "onetwothree123"  # It's a secret
from_email = username
to_list = ['']
reply = ''

f = open("report.txt", "w+")

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

# Variables Needed
numBuckets = 0
numPublicBuckets = 0
msg = ''

# Start with welcome message
printAndWrite(printWelcomeMessage(), True)

# Get credentials to access s3 account
keys = getCredentials()
printAndWrite('\n' + '–––––––––––––––– Scannning S3.... ––––––––––––––––' + '\n', True)
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
# Checks if each bucket is public or not and prints if that is true
for bucket in buckets:
    location = get_location(bucket.name, s3_client)
    # add_to_output(report_path)
    bucket_acl = bucket.Acl()
    public = check_acl(bucket_acl)
    numBuckets += 1

    msg = "Bucket:              {}".format(bucket.name)
    printAndWrite(msg, True)

    if public:
        printAndWrite('Security:            PUBLIC ! ! ! UNSECURE ! ! !', True)
        numPublicBuckets += 1
    else:
        printAndWrite('Security:            private :)', True)

    printAndWrite("Location:            {}".format(location), True)
    s3_last_used(s3_client, bucket.name)
    printAndWrite('', True)

# Prints total number of buckets and the total number of public buckets
printAndWrite(printNumBuckets(), True)
printAndWrite(printNumPublicBuckets(), True)
printAndWrite('', True)

################################# IAM ###################################

printAndWrite('- - - - - - - - - - IAM Report - - - - - - - - - - \n', True)

# Retrieve credit report
cred_report = get_cred_report()

num_users = cred_report.__len__()
printAndWrite('The number of Users (Including the Root User) is: ', False)
printAndWrite(str(num_users) + '\n', True)

# Loop through all of the IAM Users and print out
# 1. User name
# 2. Access Key Active or not
# 3. User creation Date
# 4. Password last used date
# 5. MFA Active or not
for i in range(0, num_users):
    # User Name and Whether or not the Key is active
    printAndWrite('User ' + str(i + 1) + ':      ', False)

    printAndWrite(cred_report[i]['user'], True)

    printAndWrite('             Access Key Active?:     ', False)
    if root_keys_active(cred_report, i):
        printAndWrite('Active!', True)
    else:
        printAndWrite('NOT Active.', True)

    # Access Key Last used date

    # Creation Date
    creationTime = cred_report[i]['user_creation_time']
    printAndWrite('             User Creation Date:     ' + creationTime[:10], True)

    # Password last used
    passwordLastUsed = cred_report[i]['password_last_used']
    printAndWrite('             Password Last Used:     ' + passwordLastUsed[:10], False)
    if passwordLastUsed[9:10] == 'a':
        printAndWrite('tion', True)
    else:
        printAndWrite('', True)

    # mfa Active
    printAndWrite('             MFA Active:             ' + cred_report[i]['mfa_active'], True)
    printAndWrite('', True)

printAndWrite('# # # # # # # # # # SUMMARY # # # # # # # # # #', True)
printAndWrite('', True)

# Print if root access keys are active or not
if root_keys_active(cred_report, 0):
    printAndWrite('Root Access Keys Active ! ! !', True)
else:
    printAndWrite('No Root Access Keys.', True)

# Implement Hana's code here in summary section

# Email Portion of tool -------------------------------------------------------------

printAndWrite('', True)

plain_txt = ''

# Ask user if they would like a report sent to them via email
print('\n')
ans = input('Would You like this report to be emailed to you? (Y/N): ')
print('')

# if the user input length is greater than 0, that means they inputted something
if ans.__len__() > 0:
    # If the first character is 'Y' or 'y' then the input is yes
    if ans[:1] == 'Y' or ans[:1] == 'y':

        # Add contents from report.txt file to plain_txt (str)
        with open('report.txt', 'r') as f:
            for line in f:
                plain_txt += line

        to_list[0] = input('Please enter your email: ')
        print('')
        try:
            email_conn = smtplib.SMTP(host, port)
            email_conn.ehlo
            email_conn.starttls()
            email_conn.login(username, password)

            the_msg = MIMEMultipart("alternative")
            the_msg['Subject'] = "AWS Cloud Report"
            the_msg["From"] = from_email
            # the_msg["To"] = to_list

            part_1 = MIMEText(plain_txt, 'plain')

            the_msg.attach(part_1)

            email_conn.sendmail(from_email, to_list, the_msg.as_string())
            email_conn.quit()

        except smtplib.SMTPException:
            print('Error sending message! Did not send :(')

# Print thank you message
print(thankYouMessage())
f.close()
