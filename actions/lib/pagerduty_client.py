import requests
import json

# Utility class for PagerDuty Interaction
class PagerDutyClient:

    def __init__(self, actionConfig):
        self.pack_config = actionConfig
        self.event_api_url = actionConfig['pagerduty_event_api_url']
    
    # Creates an incident using Events API
    def post_event(self, 
                   routing_key,
                   summary, 
                   source, 
                   custom_details,
                   severity="info", 
                   event_action="trigger",
                   client="UEM-StackStorm",
                   client_url="127.0.0.1"):

        headers = {
            'Content-Type': 'application/json'
        }
        event = {
            "payload": {
                "summary": summary,
                "source": source,
                "severity": severity,
                "custom_details": custom_details
            },
            "routing_key": routing_key,
            "event_action": event_action,
            "client": client,
            "client_url": client_url
        }
        payload = json.dumps(event)
        response = requests.request("POST", self.event_api_url, headers=headers, data=payload)
        if response.status_code == 202:
            print("Sent notification to PagerDuty successfully.")