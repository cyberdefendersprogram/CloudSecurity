import boto3
import time
import csv
import datetime
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def printAndWrite(msg_to_print, line_down):
    print(msg_to_print, end='')
    f.write(msg_to_print)
    if line_down:
        print('')
        f.write('\n')

def printWelcomeMessage():
    msg = '\n' + '|*||*||*||*||*| Welcome to the Snow Cloud S3 Bucket Checker |*||*||*||*||*|' + '\n'
    return msg


def thankYouMessage():
    return 'Thank you for using our snow white program!'


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
            printAndWrite('Last active date:    ', False)
            printAndWrite(str(last_activity.date()), True)
            days = datetime.datetime.now().date() - last_activity.date()
            printAndWrite('Inactive for:        ', False)
            printAndWrite(str(days), True)


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

host = "smtp.gmail.com"
port = 587
username = "cloudreport.sw@gmail.com"
password = "" # It's a secret
from_email = username
to_list = ['']
reply = ''

f = open("report.txt", "w+")


GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

numBuckets = 0
numPublicBuckets = 0
msg = ''

# Start with welcome message
printAndWrite(printWelcomeMessage(), True)

# Get credentials to access s3 account
keys = getCredentials()
printAndWrite('\n' + '–––––––––––––––– Scannning.... ––––––––––––––––' + '\n', True)
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
    printAndWrite(msg, True)

    if public:
        printAndWrite('Security:            PUBLIC ! ! ! UNSECURE ! ! !', True)
        numPublicBuckets += 1
    else:
        printAndWrite('Security:            private :)', True)

        printAndWrite("Location:            {}".format(location), True)
    s3_last_used(s3_client, bucket.name)
    printAndWrite('', True)

printAndWrite(printNumBuckets(), True)
printAndWrite(printNumPublicBuckets(), True)
printAndWrite('', True)

################################# IAM ###################################

printAndWrite('IAM Report ----------------------------------------------------- \n', True)

cred_report = get_cred_report()

num_users = cred_report.__len__()
printAndWrite('The number of Users (Including the Root User) is: ', False)
printAndWrite(str(num_users) + '\n', True)

for i in range(0, num_users):
    # User Name and Whether or not the Key is active
    printAndWrite('User' + str(i + 1) + ':       ', False)

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

printAndWrite('', True)
if root_keys_active(cred_report, 0):
    printAndWrite('Root Access Keys Active ! ! !', True)
else:
    printAndWrite('No Root Access Keys.', True)


# Email Portion of tool

printAndWrite('', True)

plain_txt = ''

with open('report.txt', 'r') as f:
    for line in f:
        plain_txt += line

ans = input('Would You like this report to be emailed to you? (Y/N): ')
print('')

if ans.__len__() > 0:
    if ans[:1] == 'Y' or ans[:1] == 'y':
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


            html_txt = """\
            <html>
                <head></head>
                <body>
                    <p>Hey!<br>
                        Testing this email <b>message</b>. Made by <a href='http://joincfe.com'>Team CFE</a>.
                    </p>
                </body>
            </html>
            """

            part_1 = MIMEText(plain_txt, 'plain')
            part_2 = MIMEText(html_txt, "html")

            the_msg.attach(part_1)
            # the_msg.attach(part_2)

            email_conn.sendmail(from_email, to_list, the_msg.as_string())
            email_conn.quit()

        except smtplib.SMTPException:
            print('Error sending message! Did not send :(')

print(thankYouMessage())