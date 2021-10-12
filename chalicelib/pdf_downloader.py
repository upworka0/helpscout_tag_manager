import os
import boto3
import base64
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
import datetime


bucket_name = os.environ.get('BUCKET_NAME')
s3 = boto3.client('s3')
user_name = os.environ.get('ACCOUNT_USERNAME')
password = os.environ.get('ACCOUNT_PASSWORD')
sendgrid_key = os.environ.get('SENDGRID_KEY')


class WebDriver:

    def __init__(self, recipient_list, sender):
        self.recipient_list = recipient_list
        self.sender = sender

        self.options = Options()
        self.options.binary_location = '/opt/headless-chromium'
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--start-fullscreen')
        self.options.add_argument('--single-process')
        self.options.add_argument('--disable-dev-shm-usage')

        self.driver = Chrome('/opt/chromedriver', options=self.options)

    # login process
    def login_process(self):
        print("Logging in now...")
        self.driver.get('https://secure.helpscout.net/')
        self.driver.find_element_by_id("email").send_keys(user_name)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("logInButton").click()

    def take_screen(self):
        S = lambda X: self.driver.execute_script('return document.body.parentNode.scroll' + X)
        self.driver.set_window_size(S('Width'), S('Height'))
        return self.driver.find_element_by_id('report-wrap').screenshot_as_png

    def send_email_with_pdf(self, pdf_data, pdf_key):
        print('Email sending ...')
        print('Recipient_list ...')
        print(self.recipient_list)
        try:
            message = Mail(
                from_email=self.sender,
                to_emails=self.recipient_list,
                subject="Email Reporting",
                html_content="Hello, This is the email report from Helpscout."
            )
            pdf_data.seek(0)
            encoded_file = base64.b64encode(pdf_data.read()).decode()

            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(pdf_key),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.add_attachment(attached_file)

            sg = SendGridAPIClient(sendgrid_key)
            response = sg.send(message)

            print(response.status_code)
            print(response.body)
            print('Success --- END')
            return {
                'status': 200,
                'key': pdf_key
            }

        except Exception as e:
            print("Error from sending email:" + str(e))
            return {
                'code': 400,
                'status': 'error',
                'error_msg': "Error from sending email:" + str(e)
            }

    def download_report_as_pdf(self, tag_id, date_from, date_to):
        self.login_process()
        res = {}
        try:
            elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "pageTitle"))  # This is a dummy element
            )
        finally:
            print("Successfully logged in")
            link = 'https://secure.helpscout.net/reports/email/?tab=responseTime&officeHours=true&channelType=email&' \
                   'rows[]=tags:{}&startDate={}&endDate={}&cmpRange=-1&cmpStartDate=&cmpEndDate='.\
                format(tag_id, date_from, date_to)
            print(link)
            self.driver.get(link)

            img = Image.open(BytesIO(self.take_screen()))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            in_mem_file = BytesIO()
            img.save(in_mem_file, format="PDF", quality=100)

            # send email with attaching pdf

            # in_mem_file.seek(0)
            # s3.put_object(Bucket=bucket_name,
            #               Key='email_pdfs/{}-{}-{}.pdf'.format(tag_id, date_from, date_to),
            #               Body=in_mem_file)

            res = self.send_email_with_pdf(in_mem_file, '{} -- {}-{}.pdf'.format(date_from, date_to, tag_id))

        self.driver.quit()

        return res
