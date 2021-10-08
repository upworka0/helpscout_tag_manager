from helpscout import HelpScout
import os

app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
helpscout_client = HelpScout(app_id=app_id, app_secret=app_secret)

keyword = 'butlercc.edu'    # query & tag name

params = 'query={}&status=active'.format(keyword)
# conversations = helpscout_client.conversations.get(params=params)

report_url = 'reports/email?start=2020-10-01T00:00:00Z&end=2021-05-31T00:00:00Z&tags=8616878'
print(helpscout_client.hit(report_url, 'get'))


def add_tag(conversation, tag_name):
    conv_id = conversation.id
    is_tag_added = False
    tags = []
    for tag in conversation.tags:
        if tag['tag'] == tag_name:
            is_tag_added = True
            break
        tags.append(tag['tag'])
    if not is_tag_added:
        # add tag to conversation
        tags.append(tag_name)
        endpoint = 'conversations/%s/tags' % conv_id
        print(tags)
        print(endpoint)
        # helpscout_client.hit(endpoint, 'put', data={'tags': tags})
        helpscout_client.conversations[conv_id].tags.put(data={'tags': tags})


def remove_tag(conversation, tag_name):
    conv_id = conversation.id
    is_tag_removed = False
    tags = []
    for tag in conversation.tags:
        if tag['tag'] == tag_name:
            is_tag_removed = True
            continue
        tags.append(tag['tag'])

    if is_tag_removed:
        endpoint = 'conversations/%s/tags' % conv_id
        print(tags)
        print(endpoint)
        # helpscout_client.hit(endpoint, 'put', data={'tags': tags})
        helpscout_client.conversations[conv_id].tags.put(data={'tags': tags})

