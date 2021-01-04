import json
import traceback

from lib import jira_client
from lib import jira_ticket

from st2common.runners.base_action import Action

class JiraIssueCreator(Action):

  DEFECT_PHASE = { "id": "16200", "value": "SRE Identified" }
  FOUND_IN_AUTOMATION = { "id": "15407", "value": "No" }

  def run(self, 
          project:str,
          type:str,
          summary:str,
          description:str,
          custom_fields:dict):

    self.jira_client = jira_client.JiraClient(self.config)
    try:
      
      # Sanitize summary
      summary = jira_client.JiraClient.replace_special_chars(summary)
      jql = "issueFunction in issueFieldMatch(\"project={0}\", \"summary\", \"{1}\")".format(project, summary)
      issues = self.jira_client.search_issues(jql)
      
      # Create/Update Issue
      if issues['total'] == 0:
        jira_key = self.__create_new(project, type, summary, description, custom_fields)
      else:
        jira_key = issues['issues'][0]['key']
        # if the issue is in 'Closed' state, we need to change it to 'Reopened'
        re_open = issues['issues'][0]['fields']['status']['name'] == 'Closed'
        if re_open:
            self.jira_client.change_status(jira_key, 'Reopened')

        if jira_key != "":
          # Update the issue regarding the additional data for the current context
          url = self.jira_client.base_url + "/issue/{0}".format(jira_key)
          payload = self.__update(project, type, summary, description, custom_fields)
          response = self.jira_client.put(url, payload)
          if (response.status_code == 204):
            print('Comments were successfully added to the new JIRA.')
          return (True, self.jira_client.base_url.replace("rest/api/latest", "browse/{0}".format(jira_key)))
    except Exception as e:
      self.logger.error("JIRA add/update failed. {0}".format(str(e)))
      traceback.print_exc()
      return (True, "JIRA add/update failed. {0}".format(str(e))) # True so that we do not stop the workflow
  
  # Creates a new JIRA issue from the given detail
  def __create_new(self, project:str, type:str, summary:str, description:str, custom_fields:dict):
    payload = self.__prepare_jira_ticket(project, 
                                          type,
                                          summary=summary, 
                                          description=description, 
                                          custom_fields=custom_fields)
    url = self.jira_client.base_url + '/issue'
    response = self.jira_client.post(url, payload)
    result = json.loads(response.text)
    if (response.status_code == 201):
        key = result['key']
        print("New JIRA ticket {0} has been created successfully".format(key))
        return key
    else:
        print('Failed to create JIRA. Error: {0}'.format(json.loads(response.text)))
        return ""
    
  # Initialize JIRA ticket data from the given detail
  def __prepare_jira_ticket(self, project, type:str, summary:str, description:str, custom_fields:dict):
    # Payload creation
    data = {
        "update": { 
            "description": [{"set": description}]
            , "versions": [{"add": { "name": custom_fields["affected_version"] }}]
        },
        "fields": {
            "summary": summary,
            "project": { "key": project },
            "issuetype": { "name": type },
            "priority": custom_fields["priority"],
            "components": custom_fields["components"], 
            "customfield_12800": custom_fields["severity"],
            "customfield_13000": JiraIssueCreator.DEFECT_PHASE,
            "customfield_14300": JiraIssueCreator.FOUND_IN_AUTOMATION, 
            "labels": custom_fields["labels"],
            "assignee": None
        }
    }

    if project == "SRE": # SRE project does NOT have affected version field with any values
        data["update"].pop("versions")

    payload = json.dumps(data)

    return payload

  # Updates the JIRA ticket with data
  def __update(self, project:str, type:str, summary:str, description:str, custom_fields:dict):
    data = {
            "update": {
                "comment": [
                    { 
                        "add": 
                        { 
                            "body": description
                        }
                    }
                ]
                , "versions": [{"add": { "name": custom_fields["affected_version"] }}]
        },
        "fields": {
            "labels": custom_fields["labels"]
        }
    }
    if project == "SRE": # SRE project does NOT have affected version field with any values
        data["update"].pop("versions")
    payload = json.dumps(data)
    return payload