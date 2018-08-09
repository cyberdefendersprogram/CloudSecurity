# the email part
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initial information for email setup
host = "smtp.gmail.com"
port = 587
username = "cloudreport.sw@gmail.com"
password = "onetwothree123"  # It's a secret
from_email = username
to_list = ['']
reply = ''



# Email Portion of tool -------------------------------------------------------------

def main():

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