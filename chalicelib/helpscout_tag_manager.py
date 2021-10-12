class TagManager:
    helpscout_client = None
    tag_id = None
    tag_name = None
    access_token = None

    def __init__(self, helpscout_client):
        self.helpscout_client = helpscout_client
        self.auth()

    def auth(self):
        print('Authenticating ...')
        if self.helpscout_client.access_token is None:
            self.helpscout_client._authenticate()
        self.access_token = self.helpscout_client.access_token

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
            print(conv_id)
            # add tag to conversation
            print('Adding tags to conversation {}'.format(conv_id))
            self.helpscout_client.conversations[conv_id].tags.put(data={'tags': tags})

        return conv_id

    def get_tag_id(self, conv_id):
        if self.tag_id is None:
            endpoint = 'conversations/{}'.format(conv_id)
            conversation = self.helpscout_client.get_objects(endpoint)
            for tag in conversation[0].tags:
                if tag['tag'] == self.tag_name:
                    self.tag_id = tag['id']
                    return

    def get_email_report(self, start, end):
        report_url = 'reports/email?start=2020-10-01T00:00:00Z&end=2021-09-30T00:00:00Z&tags=%s' % self.tag_id
        res = next(self.helpscout_client.hit_(report_url, 'get'))
        print(res)

    def process(self, tag_name, date_from=None, date_to=None):
        self.tag_name = tag_name
        params = 'query={} waitingSince:[{} TO {}]&status=all'.format(self.tag_name, date_from, date_to)
        print(params)
        conversations = self.helpscout_client.conversations.get(params=params)
        print(len(conversations))

        conv_id = None
        for conv in conversations:
            conv_id = self.add_tag(conv)

        self.get_tag_id(conv_id)
        print("Tag id is {}".format(self.tag_id))
        return self.tag_id
        # self.get_email_report('2020-10-01T00:00:00Z', '2021-09-31T00:00:00Z')
        # self.get_email_report(date_from, date_to)

