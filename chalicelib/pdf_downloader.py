"""
This Helper allows you to download Email report page on Helpscout as pdf format
and send email with it via Python.
"""

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


# Retrieving env variables
bucket_name = os.environ.get('BUCKET_NAME')
user_name = os.environ.get('ACCOUNT_USERNAME')
password = os.environ.get('ACCOUNT_PASSWORD')
sendgrid_key = os.environ.get('SENDGRID_KEY')

s3 = boto3.client('s3')


class WebDriver:
    """
        Wrapper to take the screenshot of email report page on Helpscout, convert it to pdf and send email with it
    """

    def __init__(self, recipient_list, sender, app):
        """
        Constructor of Wrapper

        :param recipient_list: array : recipients' email list
        :param sender: string:  sender email
        :param app: Chalice app for logging
        """
        self.app = app

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

    # login process via chrome driver
    def login_process(self):
        self.app.log.info("Logging in now...")
        self.driver.get('https://secure.helpscout.net/')
        self.driver.find_element_by_id("email").send_keys(user_name)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("logInButton").click()

    def take_screen(self):
        """
        Takes the whole screen of page as png format
        :return: Byte
        """
        S = lambda X: self.driver.execute_script('return document.body.parentNode.scroll' + X)
        self.driver.set_window_size(S('Width'), S('Height'))
        return self.driver.find_element_by_id('report-wrap').screenshot_as_png

    def send_email_with_pdf(self, pdf_data, pdf_key):
        """
        Sends email to recipients
        :param pdf_data: Byte
        :param pdf_key: string
        :return: dict
        """
        self.app.log.info('Email sending ...')
        self.app.log.info('Recipient_list ...')
        self.app.log.info(self.recipient_list)
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

            self.app.log.info(response.status_code)
            self.app.log.info(response.body)
            self.app.log.info('Success --- END')
            return {
                'status': 200,
                'key': pdf_key
            }

        except Exception as e:
            self.app.log.info("Error from sending email:" + str(e))
            return {
                'code': 400,
                'status': 'error',
                'error_msg': "Error from sending email:" + str(e)
            }

    def process(self, tag_id, date_from, date_to):
        """
        Main process step: Login to helpscout website, visit Email report page, take screenshot, convert it pdf format
        and sending email with it to the all recipients.
        :param tag_id: int : the id of custom tag
        :param date_from: string
        :param date_to: string
        :return: dict
        """
        self.login_process()
        res = {}
        try:
            elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "pageTitle"))  # This is a dummy element
            )
        finally:
            self.app.log.info("Successfully logged in")
            link = 'https://secure.helpscout.net/reports/email/?tab=responseTime&officeHours=false&channelType=email&' \
                   'rows[]=tags:{}&startDate={}&endDate={}&cmpRange=-1&cmpStartDate=&cmpEndDate='.\
                format(tag_id, date_from, date_to)
            self.app.log.info(link)
            self.driver.get(link)

            img = Image.open(BytesIO(self.take_screen()))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            in_mem_file = BytesIO()
            img.save(in_mem_file, format="PDF", quality=100)

            # in_mem_file.seek(0)
            # s3.put_object(Bucket=bucket_name,
            #               Key='email_pdfs/{}-{}-{}.pdf'.format(tag_id, date_from, date_to),
            #               Body=in_mem_file)

            # send email with attaching pdf
            res = self.send_email_with_pdf(in_mem_file, '{} -- {}-{}.pdf'.format(date_from, date_to, tag_id))

        self.driver.quit()

        return res
