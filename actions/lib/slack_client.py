import requests

# Utility class for Slack Interaction
class SlackClient:

    def __init__(self, actionConfig):
        self.pack_config = actionConfig
    
    # On-demand slack message notification
    def post_message_to_channel(self, message, identifier, url=''):
        headers = {
            'Content-Type': 'application/json'
        }

        if identifier in self.pack_config:
            url = self.pack_config[identifier]
        
        if len(url) > 0:
            response = requests.request("POST", url, headers=headers, data=message)
            if response.status_code == 200:
                print("Sent notification to {0} slack successfully.".format(str(identifier)))

    
    def invoke_webhook(self, url, message):
        headers = {
            'Content-Type': 'application/json'
        }
        if len(url) > 0:
            response = requests.request("POST", url, headers=headers, data=message, verify=False)
            if response.status_code != 200:
                print("Slack notification failed. Reason: {0}".format(response.text))