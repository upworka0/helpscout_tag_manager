import os
from chalice import Chalice
import logging
from chalicelib.helpscout_tag_manager import TagManager
from chalicelib.pdf_downloader import WebDriver
from dateutil import parser


app = Chalice(app_name='helpscout')
# Enable DEBUG logs.
app.log.setLevel(logging.DEBUG)


# get Env variables
app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')


# convert datetime to ISO format for api request
def convert_ISO_format(dt):
    date_time = parser.parse(dt)
    return date_time.replace(microsecond=0).isoformat() + 'Z'


@app.route('/', methods=['POST'])
def index():
    header_data = app.current_request.headers
    if header_data.get('x-api-key', '').upper() != 'XXXXXXX':
        return {
            "status": "Error",
            "message": "Not Authorized, custom auth missing"
        }

    request_body = app.current_request.json_body
    app.log.info('Handler triggered ...')
    app.log.info(request_body)

    date_from = request_body.get('date_from')
    date_to = request_body.get('date_to')
    sender = request_body.get('sender', None)
    recipient_list = request_body.get('recipient_list', [])
    tag_name = request_body.get('tag_name')

    try:
        manager = TagManager(app_id=app_id, app_secret=app_secret, app=app)
        tag_id = manager.process(tag_name)

        driver = WebDriver(sender=sender, recipient_list=recipient_list, app=app)
        return driver.process(tag_id=tag_id, date_to=date_to)

    except Exception as e:
        return {
            'status': 400,
            'message': str(e)
        }
