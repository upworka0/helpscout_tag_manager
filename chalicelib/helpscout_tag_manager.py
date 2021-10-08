from helpscout import HelpScout


class TagManager:

    helpscout_client = None
    app_id = None
    app_secret = None
    access_token = None
    tag_id = None
    tag_name = None

    def __init__(self, app_id, app_secret, access_token=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.helpscout_client = HelpScout(app_id=self.app_id, app_secret=self.app_secret)
        self.helpscout_client.access_token = self.access_token
        self.auth()

    def auth(self):
        print('Authenticating ...')
        if self.helpscout_client.access_token is None:
            self.helpscout_client._authenticate()
            self.access_token = self.helpscout_client.access_token
        print('Access_token: %s' % self.access_token)

    def add_tag(self, conversation):
        conv_id = conversation.id
        not_tag_added = True
        tags = [self.tag_name]
        for tag in conversation.tags:
            if tag['tag'] == self.tag_name:
                not_tag_added = False
                self.tag_id = tag['id']
                break
            tags.append(tag['tag'])
        if not_tag_added:
            # add tag to conversation
            endpoint = 'conversations/%s/tags' % conv_id
            print(tags)
            print(endpoint)
            self.helpscout_client.conversations[conv_id].tags.put(data={'tags': tags})

        return conv_id

    def get_tag_id(self, conv_id):
        if self.tag_id is None:
            endpoint = 'conversations/{}'.format(conv_id)
            conversation = self.helpscout_client.get_objects(endpoint)
            print(conversation[0].tags)
            for tag in conversation[0].tags:
                if tag['tag'] == self.tag_name:
                    self.tag_id = tag['id']
                    return

    def get_email_report(self, start, end):
        report_url = 'reports/email?start=2020-10-01T00:00:00Z&end=2021-09-30T00:00:00Z&tags=%s' % self.tag_id
        print(report_url)
        res = next(self.helpscout_client.hit_(report_url, 'get'))
        # res = self.helpscout_client.hit(report_url, 'get')
        print(res)

    def process(self, keyword):
        self.tag_name = keyword
        params = 'query={}&status=pending'.format(keyword)
        conversations = self.helpscout_client.conversations.get(params=params)

        conv_id = None
        for conv in conversations:
            conv_id = self.add_tag(conv)

        self.get_tag_id(conv_id)

        self.get_email_report('2020-10-01T00:00:00Z', '2021-09-31T00:00:00Z')
