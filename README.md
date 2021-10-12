# helpscout_tag_manager
This helper is to add custom tag to the all conversations by query and extract Email report data on Helpscout.<br> 
This project is using python-helpscout-v2, selenium and chalice python packages and deployed as AWS lambda function.
     
## Testing
    - The api endpoint is following.
        https://ytiumqj8ta.execute-api.us-west-1.amazonaws.com/api/
    - The request payload should be like this.
        {
            "date_from":"2020-10-01",
            "date_to": "2021-09-30",
            "tag_name": "butlercc.edu",
            "recipient_list": ["upworka0@gmail.com"],
            "sender": "upworka0@gmail.com"
        }
    