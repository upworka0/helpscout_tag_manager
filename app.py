import os
from chalice import Chalice
from helpscout import HelpScout
from chalicelib.helpscout_tag_manager import TagManager


app = Chalice(app_name='helpscout')
app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
helpscout_client = HelpScout(app_id=app_id, app_secret=app_secret)
helpscout_client._authenticate()
print(helpscout_client.access_token)


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

    keyword = request_body['keyword']
    method = request_body['method']

    try:
        manager = TagManager(app_id, app_secret, helpscout_client.access_token)
        manager.process('butlercc.edu')
    except Exception as e:
        return {
            'status': 400,
            'message': str(e)
        }

    return {'status': 200}
