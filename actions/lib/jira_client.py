import requests
import json
import re
from requests.auth import HTTPBasicAuth

class JiraClient: 
    
    def __init__(self, actionConfig):
        self.base_url = actionConfig["jira_api_url"]
        self.auth=HTTPBasicAuth(actionConfig['jira_username'], actionConfig['jira_password'])
    
    def search_issues(self, jql):
        url = self.base_url + "/search"
        payload = json.dumps({ "jql": jql })
        response = self.post(url, payload=payload)
        issue = json.loads(response.text)
        return issue

    def change_status(self, issue_key, status):
        url = self.base_url + "/issue/{0}/transitions?expand=transitions.fields".format(issue_key)
        transition_id = self.get_transition_id(url, 'To Do')
        transition_data = json.dumps({
            "transition": {
                "id": transition_id
            }
        })
        transition_response = self.post(url, payload=transition_data)
        if transition_response.status_code != 204:
            print("API returned bad status code : %s." % transition_response.status_code)
            print("API response : %s" % transition_response.text)

    def get_transition_id(self, url, status):
        response = self.get(url)
        response = json.loads(response.text)
        for transition in response['transitions']:
            if transition['to']['statusCategory']['name'] == status:
                return transition['id']

    def get(self, url):
        headers = {
            "Accept": "application/json"
        }
        response = requests.request("GET", url, headers=headers, auth=self.auth)
        return response

    def post(self, url, payload):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, data=payload, headers=headers, auth=self.auth)
        return response
    
    def put(self, url, payload):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.request("PUT", url, data=payload, headers=headers, auth=self.auth)
        return response
    
    # JQL does not work well with special characters...
    # Ref: https://jira.atlassian.com/browse/JRASERVER-25092?_ga=2.222556125.750956468.1585772419-601946177.1574782175
    @staticmethod
    def replace_special_chars(orig_text:str):
        valid_text = re.sub(r'[^a-zA-Z0-9\-\_\n\.]', ' ', orig_text)
        return valid_text
    
    # Derive Affected Version for JIRA Ticket
    @staticmethod
    def derive_affected_version(version:str):
        pattern = re.compile(r"^([1-9]\d)\.(1[012]|[1-9]|0)\.\d{1,}\.(\d{1,})$")
        match = re.search(pattern, version)
        if match:
            parts = version.split(".")
            major = parts[0]
            minor = parts[1]
            if len(minor) == 1:
                return major + minor.zfill(2)
            return major + minor
        raise ValueError("'{0}' is not a valid UEM version.".format(version))
            





        