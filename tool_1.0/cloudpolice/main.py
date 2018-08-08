import boto3
import rootuserMonitor 
import publicBucketChecker
import iamMonitor


def getCredentials():
	accessKey = input("AWS Access Key ID?: ")
	secretKey = input("AWS Secret Access Key?: ")
	return [accessKey, secretKey]


def printAndWrite(msg, changeLine):
    """
    Prints to the console and writes to the file
    – Input: msg_to_print: (str) message, line_down (boolean)
    """
    print(msg, end = '')
    f.write(msg)
    
    if changeLine:
        print('')
        f.write('\n')


if __name__ == "__main__":

	# –– Initial Set up ––
	# Get credentials to access s3 account
	keys = getCredentials()
	ACCESS_KEY = keys[0]
	SECRET_KEY = keys[1]

	GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
	}

	# Define S3 as the AWS service that we are goign to use
	s3 = boto3.resource("s3", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)
	
	# Provide credentials to boto3
	s3_client = boto3.client("s3", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)
	cloudtrail_client = boto3.client('cloudtrail', aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)
	iam_client = boto3.client("iam", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)


	welcomeMsg = '\n' + '|*||*||*||*||*| Welcome to the Snow Cloud S3 Bucket Checker |*||*||*||*||*|' + '\n'
	thankyouMsg = 'Thank you for using our snow white program!'

	f = open("report.txt", "w+")

	# Start with welcome message 
	printAndWrite(welcomeMsg, True)

	#  Start Scanning Session
	print('\n' + '>>>>>>>>>>>> Scannning.... >>>>>>>>>>>' + '\n')

	print('\n' + '–––––––––––––––– S3 Bucket Check ––––––––––––––––' + '\n')
	publicBucketChecker.main(s3, s3_client, GROUPS_TO_CHECK)

	print('\n' + '–––––––––––––––– IAM Check ––––––––––––––––' + '\n')
	iamMonitor.main(iam_client)

	print('\n' + '–––––––––––––––– Root User Check ––––––––––––––––' + '\n')
	rootuserMonitor.main(cloudtrail_client)


	printAndWrite(thankyouMsg, True)
	print ("")
	print ("")









	



















# # Get all s3 buckets 
# buckets = s3.buckets.all()

# # Get info of each bucket
# for bucket in buckets:
#     # get location of bucket 
#     location = get_location(bucket.name, s3_client)
#     # retrieve the policy grant info
#     bucket_acl = bucket.Acl()
#     public = check_acl(bucket_acl)
#     numBuckets += 1

#     # render message
#     msg = "Bucket:              {}".format(bucket.name)
#     printAndWrite(msg, True)

#     if public:
#         printAndWrite('Security:            PUBLIC ! ! ! UNSECURE ! ! !', True)
#         numPublicBuckets += 1
#     else:
#         printAndWrite('Security:            private :)', True)
    
#     printAndWrite("Location:            {}".format(location), True)
#     s3_last_used(s3_client, bucket.name)
#     printAndWrite('', True)


# # Prints total number of buckets and the total number of public buckets
# printAndWrite(printNumPublicBuckets(), False)
# printAndWrite(printNumBuckets(), True)
# printAndWrite('\n', True)
