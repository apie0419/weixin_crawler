from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header         import Header
from smtplib              import SMTP
from datetime             import date, timedelta

import traceback, os, tarfile, configparser


base_path = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.optionxform = str
config.read(os.path.join(base_path, '../setting.conf'), encoding='utf-8')

user     = config.get("MAIL", "USER")
password = config.get("MAIL", "PASSWORD")
to       = config.get("MAIL", "RECIEVER")


def Send_Mail(start, end):

	with tarfile.open(os.path.join(base_path, "../Outputs/" + str(start) + "~" + str(end) + "_output.tar.gz"), "w:gz") as tf:
		for file in os.listdir(os.path.join(base_path, "../Outputs")):
			if str(start) + "~" + str(end) in file:
				tf.add(os.path.join(base_path, "../Outputs/" + file), arcname = file)

	subject = "Weixin Research Weekly Report"

	mul_msg = MIMEMultipart()
	mul_msg['From'] = user
	mul_msg['To'] = to
	mul_msg['Subject'] = Header(subject, 'utf-8')

	file_path = os.path.join(base_path, "../Outputs/" + str(start) + "~" + str(end) + "_output.tar.gz")

	att1 = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
	att1['Content-Type'] = 'application/octet-stream'
	att1["Content-Disposition"] = 'attachment;filename="output.tar.gz"'
	mul_msg.attach(att1)

	try:
		smtpObj = SMTP('smtp.gmail.com', 587)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.login(user, password)
		smtpObj.sendmail(mul_msg["From"], mul_msg["To"].split(","), mul_msg.as_string())
		smtpObj.close()
	except:
		traceback.print_exc()

if __name__ == '__main__':
	start = date(2019, 9, 2)
	end = date(2019, 9, 8)
	Send_Mail(start, end)
