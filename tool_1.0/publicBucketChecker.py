
import boto3

# pakages = ["boto3", "termcolor"]

# "package sth couldn't be loaded, please do pip install ", "package" 

# def getPackage(package):
# 	import importlib

# 	try:
# 		importlib.import_module(pkg)
# 	except ImportError:
# 		import pip
# 		print("Installing ", str(pkg))
# 		pip.




def getCredentials():
	accessKey = input("AWS Access Key ID? ")
	secretKey = input("AWS Secret Access Key? ")

	return [accessKey, secretKey]

keys = getCredentials()

# Define S3 as the AWS service that we are goign to use
s3 = boto3.resource('s3', aws_access_key_id = keys[0], aws_secret_access_key = keys[1])

# Provide credentials to boto3
s3Client = boto3.client('s3', aws_access_key_id = keys[0], aws_secret_access_key = keys[1])



###––– yay, let's do something with it! –––###

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

# Print out bucket location
# TBB

