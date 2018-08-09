import boto3

def listIAMusers(temp_access_storage, temp_secret_storage, client):
    
    print("List of IAM users on your accounts: ")

    user_list = []
    users = client.list_users()   

    print (users)


    # {'Users': [
    #     {'Path': '/', 
    #     'UserName': 'admin', 
    #     'UserId': 'str', 
    #     'Arn': 'str', 
    #     'CreateDate': datetime.datetime(2018, 7, 23, 22, 25, 29, tzinfo=tzutc()), 
    #     'PasswordLastUsed': datetime.datetime(2018, 7, 31, 18, 15, 11, tzinfo=tzutc())}
    #     ], 
    #     'IsTruncated': False, 
    #     'ResponseMetadata': 
    #         {'RequestId': 'str', 
    #         'HTTPStatusCode': 200, 
    #         'HTTPHeaders': 
    #             {'x-amzn-requestid': 'str', 
    #             'content-type': 'text/xml', 
    #             'content-length': '613', 
    #             'date': 'Mon, 06 Aug 2018 18:30:05 GMT'}, 
    #         'RetryAttempts': 0}
    #     }

    # {'Users': [
    #     {'Path': '/', 
    #     'UserName': 'admin', 
    #     'UserId': 'AIDAIYJEMJCGY7EJFBICC', 
    #     'Arn': 'arn:aws:iam::129135059066:user/admin', 
    #     'CreateDate': datetime.datetime(2018, 7, 23, 22, 25, 29, tzinfo=tzutc()), 
    #     'PasswordLastUsed': datetime.datetime(2018, 7, 31, 18, 15, 11, tzinfo=tzutc())
    #     }, 
    #     {'Path': '/', 
    #     'UserName': 'test', 
    #     'UserId': 'AIDAJHD7TCWQ5OHIIL3FG', 
    #     'Arn': 'arn:aws:iam::129135059066:user/test', 
    #     'CreateDate': datetime.datetime(2018, 8, 6, 18, 38, 12, tzinfo=tzutc())}], 
    #     'IsTruncated': False, 
    #     'ResponseMetadata': 
    #         {'RequestId': '00455836-99a8-11e8-a09c-5dff10488e54', 
    #         'HTTPStatusCode': 200, 
    #         'HTTPHeaders': 
    #             {'x-amzn-requestid': '00455836-99a8-11e8-a09c-5dff10488e54', 
    #             'content-type': 'text/xml', 
    #             'content-length': '857', 
    #             'date': 'Mon, 06 Aug 2018 18:39:06 GMT'}, 
    #         'RetryAttempts': 0}
    #     }

    # for key in users['Users']:
    #     result = {}
    #     policies = []
    #     groups = []

    #     result['userName'] = key['UserName']
    #     list_of_policies = client.list_user_policies(UserName = key['UserName'])

    #     result['Policies'] = list_of_policies['PolicyNames']

    #     list_of_groups = client.list_groups_for_user(UserName = key['UserName'])

#     for Group in list_of_groups['Groups']:
#         Groups.append(Group['GroupName'])
#     result['Groups'] = Groups

#     list_of_mfa_devices = client.list_mfa_devices(UserName = key['UserName'])

#     if not len(list_of_mfa_devices['MFADevices']):
#     result['MFA Configured'] = False
#     else:
#     result['MFA Configured'] = True
#     user_list.append(result)

    # for key in user_list:
    # print(key)


def paginatorfunct():
    # Create IAM client
    iam = boto3.client('iam')

    # List users with the pagination interface
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        print(response)


def getCredentials():
    accessKey = input("AWS Access Key ID?: ")
    secretKey = input("AWS Secret Access Key?: ")

    return [accessKey, secretKey]


##################[ FUNCTION CALLS ]##################

keys = getCredentials()
access_key = keys[0]
secret_key = keys[1]

iam_client = boto3.client('iam', aws_access_key_id = access_key, aws_secret_access_key = secret_key)

listIAMusers(access_key, secret_key, iam_client)