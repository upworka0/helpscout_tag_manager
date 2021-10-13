"""
This Helper allows you to add custom tag to Conversations on Helpscout via Python.

For more information ,see here.
https://developer.helpscout.com/mailbox-api/endpoints/conversations/update/

"""

from helpscout import HelpScout


class TagManager:
    helpscout_client = None
    tag_id = None
    tag_name = None
    access_token = None

    def __init__(self, app_id, app_secret, app):
        """
        Construct the TagManager object.

        :param app_id: string: APP_ID of Helpscout developer app, value will be read from environment variable "APP_ID"
        :param app_secret: string : APP_SECRET of Helpscout developer app,
                            value will be read from environment variable "APP_SECRET",
        More details here  https://developer.helpscout.com/mailbox-api/overview/authentication/

        :param app: Chalice application for logging
        """
        self.app = app
        self.helpscout_client = HelpScout(app_id=app_id, app_secret=app_secret)
        self.auth()

    def auth(self):
        """
        HelpScout Authentication
        :return: None
        """
        self.app.log.info('Authenticating ...')
        if self.helpscout_client.access_token is None:
            self.helpscout_client._authenticate()
        self.access_token = self.helpscout_client.access_token

    def add_tag(self, conversation):
        """
        Add custom tag to the conversation

        :param conversation: conversation object
        :return: conversation id
        """
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
            self.app.log.info('Adding tags to conversation [{}]'.format(conv_id))
            self.helpscout_client.conversations[conv_id].tags.put(data={'tags': tags})

        return conv_id

    def get_tag_id(self, conv_id):
        """
        Retrieve Tag's Id from Conversation object with its id

        :param conv_id: int: Conversation id
        :return: int : tag id
        """
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
        self.app.log.info(res)

    def process(self, tag_name, date_from=None, date_to=None):
        """
        Main process function, to add new custom tag to all conversations by query and return custom tag's id

        :param tag_name: string : Custom tag name
        :param date_from: string
        :param date_to: string
        :return: int
        """
        self.tag_name = tag_name
        # params = 'query={} waitingSince:[{} TO {}]&status=all'.format(self.tag_name, date_from, date_to)
        params = 'query={}&status=all'.format(self.tag_name)
        self.app.log.info(params)
        conversations = self.helpscout_client.conversations.get(params=params)
        self.app.log.info("Conversation count is {}".format(len(conversations)))

        conv_id = None
        for conv in conversations:
            conv_id = self.add_tag(conv)

        self.get_tag_id(conv_id)
        self.app.log.info("Tag id is {}.".format(self.tag_id))
        return self.tag_id
        # self.get_email_report('2020-10-01T00:00:00Z', '2021-09-31T00:00:00Z')
        # self.get_email_report(date_from, date_to)

