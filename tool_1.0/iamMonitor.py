import boto3
import time
import csv
import datetime
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
def get_cred_report(iam_client):
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


def main(iam_client):
    # Retrieve credit report
    cred_report = get_cred_report(iam_client)

    num_users = cred_report.__len__()
    print('The number of Users (Including the Root User) is: ', str(num_users) + '\n')

    # Loop through all of the IAM Users and print out
    # 1. User name
    # 2. Access Key Active or not
    # 3. User creation Date
    # 4. Password last used date
    # 5. MFA Active or not
    for i in range(0, num_users):
        # User Name and Whether or not the Key is active
        print('User ' + str(i + 1) + ':      ', end='')

        print('arn:                    ' + str(cred_report[i]['arn']))

        # print('             Access Key Active?:     ')
        if root_keys_active(cred_report, i):
            print('             Access Key Active?:     '+'Active!')
        else:
            print('             Access Key Active?:     '+'NOT Active.')

        # Access Key Last used date

        # Creation Date
        creationTime = cred_report[i]['user_creation_time']
        print('             User Creation Date:     ' + creationTime[:10])

        # Password last used
        passwordLastUsed = cred_report[i]['password_last_used']
        print('             Password Last Used:     ', end='')
        if passwordLastUsed[9:10] == 'a':
            print('No Information')
        else:
            print(passwordLastUsed[:10])

        print('             Key 1 Last Service:     ' + cred_report[i]['access_key_1_last_used_service'])
        print('             Key 2 Last Service:     ' + cred_report[i]['access_key_2_last_used_service'])

        # mfa Active
        print('             MFA Active:             ' + cred_report[i]['mfa_active'])
        print('')
