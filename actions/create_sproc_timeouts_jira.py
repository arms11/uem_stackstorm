import json

from lib import jira_client
from lib import jira_ticket
from st2common.runners.base_action import Action

class CreateSprocTimeoutsJiraAction(Action):

    def run(self, alert_detail):
        self.jira_client = jira_client.JiraClient(self.config)
        try:
            for detail in alert_detail["detail"]:
                ######## TODO: Add <StoredProcedureName> below to be searched...
                summary = self.jira_client.replace_special_chars("{0} {1}".format(detail["environment"], alert_detail["title"]))
                project = '<UEM_PROJECT>' ###### TODO: Extrapolate the UEM Project from the Mapping
                jql = "issueFunction in issueFieldMatch(\"project={0}\", \"summary\", \"{1}\")".format(project, summary)
                issues = self.jira_client.search_issues(jql)

                if issues['total'] == 0:
                    issue_key = self.__create_new(summary, alert_detail["description"], detail["version"], detail["count"])
                    if issue_key:
                        detail["jira_key"] = issue_key
                else:
                    issue_key = issues['issues'][0]['key']
                    # if the issue is in 'Done' state, we need to change it to 'To Do'
                    re_open = issues['issues'][0]['fields']['status']['statusCategory']['id'] == 3
                    issue_key = self.__update_existing(issue_key, re_open, detail["version"], detail["count"])
                    if issue_key:
                        detail["jira_key"] = issue_key

            return (True, alert_detail)
        except Exception as e:
            print('Exception occurred: {ex}'.format(ex=str(e)))
            return (False, alert_detail)

    def __prepare_jira_ticket(self, summary:str, description:str, detail:dict):

        ticket = jira_ticket.UemJiraTicket(project_id = 16606, #######TODO: Extrapolate the UEM Project from the Mappings
                                           summary = summary, 
                                           description = description,
                                           priority = { "id": "3" }, # P2
                                           severity = { "id": "13302", "value": "Serious" }, # Severity
                                           component = { "id": "21903" }) # SRE Bugs
        # Payload creation
        payload = json.dumps( 
                    {
                        "update": { "description": [{"set": ticket.description}] },
                        "fields": {
                            "summary": ticket.summary,
                            "project": ticket.project_id,
                            "issuetype": ticket.issue_type,
                            "priority": ticket.priority,
                            "components": ticket.components, 
                            "customfield_12800": ticket.severity,
                            "customfield_13000": ticket.defect_phase,
                            "customfield_14300": ticket.found_in_automation,
                            "labels": ticket.labels
                        }
                    }
                )

        return payload

    def __prepare_comment(self, version:str, count:int):
        payload = json.dumps(
            {
                "update": {
                    "comment": [{"add": { "body": "WS1 Version: {0}, Number of events: {1}".format(version, count) }}]
                }
            }
        )
        return payload

    def __create_new(self, summary:str, description:str, version:str, count:int):
        payload = self.__prepare_jira_ticket(summary=summary, 
                                            description=description,
                                            detail =
                                            {
                                                "version": version,
                                                "count": count
                                            })
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

    def __update_existing(self, issue_key:str, re_open:bool, version:str, count:int):

        if re_open:
            self.jira_client.change_status(issue_key, 'To Do')

        url = self.jira_client.base_url + "/issue/{0}".format(issue_key)
        payload = self.__prepare_comment(version, count)
        response = self.jira_client.put(url, payload)
        if (response.status_code == 204):
            print('JIRA was updated successfully.')
            return issue_key
        else:
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
            return ""