import json
import traceback

from lib import jira_client
from lib import jira_ticket
from lib import slack_client
from lib import logz_alert_sample_parser

from st2common.runners.base_action import Action

class SprocTimeoutAlertAutomationWorkflow(Action):
  
    def run(self, title, description, severity, event_data, mappings):
        print("Alert Name: {0}".format(title))
        samples = logz_alert_sample_parser.LogzAlertSamplesParser.get_samples(event_data)
        mappings = self.__normalize_keys(mappings)
        self.jira_client = jira_client.JiraClient(self.config)
        alert_detail = { "title" : title, "description": description, "severity": severity, "context": [] }
        self.slackClient = slack_client.SlackClient(self.config)
        for sample in samples:
            try:
                envt = sample["fields.env_name"]
                sproc = sample["StoredProcedureName"]
                version = sample["fields.ws1_release"]
                count = sample["count"]
                labels = ["sre_monitoring", "sproc-timeout", envt, version]
                jira_key = None

                # Find the existing issue....if none exists, create one
                project = self.__derive_uem_project_from_sproc(sproc, mappings=mappings)
                affected_version = jira_client.JiraClient.derive_affected_version(version)
                summary = jira_client.JiraClient.replace_special_chars("{0} {1}".format(sproc, title))
                print(summary)
                jql = "issueFunction in issueFieldMatch(\"project={0}\", \"summary\", \"{1}\")".format(project, summary)
                issues = self.jira_client.search_issues(jql)

                if issues['total'] == 0:
                    jira_key = self.__create_new(project, summary, description, detail=
                                                    { 
                                                        "project": project, 
                                                        "labels": labels, 
                                                        "envt": envt,
                                                        "affected_version": affected_version,
                                                        "version": version,
                                                        "count": count
                                                    })                    
                else:
                    jira_key = issues['issues'][0]['key']
                    # if the issue is in 'Closed' state, we need to change it to 'Reopened'
                    re_open = issues['issues'][0]['fields']['status']['name'] == 'Closed'
                    if re_open:
                        self.jira_client.change_status(jira_key, 'Reopened')
                    self.__update_existing(jira_key, 
                                            re_open, 
                                            detail=
                                            { 
                                                "project": project, 
                                                "labels": labels, 
                                                "envt": envt,
                                                "affected_version": affected_version,
                                                "version": version,
                                                "count": count
                                            })
                if jira_key:
                    # Store context data to be used in the notification later
                    alert_detail["context"].append({
                        "sproc": sproc,
                        "jira_key": self.jira_client.base_url.replace("rest/api/latest", "browse/{0}".format(jira_key)),
                        "envt": envt,
                        "version": version,
                        "count": count
                    })
            except Exception as e:
                self.logger.error("JIRA add/update failed. {0}".format(str(e)))
                traceback.print_exc()

        # Notify SRE Slack Channel
        self.__notify_sre(alert_detail)
        
        return (True, alert_detail)

    def __notify_sre(self, alert_detail:dict):
        if len(alert_detail["context"]) > 0:
            message = { "blocks": [] }
            message["blocks"].append({
                        "type": "header",
                        "text": { "type": "plain_text", "text": alert_detail["title"] }
                    })
            for sample in alert_detail["context"]:
                message["blocks"].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*{0}*\n>Environment: _{1}_\n>Version: _{2}_\n>Count: _{3}_\n>JIRA: {4}"
                                    .format(sample["sproc"], sample["envt"], sample["version"], sample["count"], sample["jira_key"])
                        }
                    }
                )
                message["blocks"].append({ "type": "divider" })
            payload = json.dumps(message)
            self.slackClient.post_message_to_channel(payload, 'slack_sre_alert_channel_url')

    def __normalize_keys(self, mappings:dict):
        normalized = {}
        for k, v in mappings.items():
            normalized[k.lower()] = v
        return normalized

    def __derive_uem_project_from_sproc(self, sprocName:str, mappings:dict):
        if sprocName and sprocName.strip():
            if(sprocName.find('.')) != -1:
                schema = sprocName.split('.')[0].lower() # ignore case
                if schema.lower() == "dbo" or schema.lower() == "mobilemanagement":
                    return "SRE"
                return mappings[schema]
            return "SRE"
        raise ValueError("SprocName is invalid or not provided.")

    def __create_new(self, project:str, summary:str, description:str, detail:dict):
        payload = self.__prepare_jira_ticket(project, 
                                             summary=summary, 
                                             description=description, 
                                             labels=detail["labels"], 
                                             affected_version=detail["affected_version"])
        url = self.jira_client.base_url + '/issue'
        response = self.jira_client.post(url, payload)
        result = json.loads(response.text)
        if (response.status_code == 201):
            key = result['key']
            print("New JIRA ticket {0} has been created successfully".format(key))
            # Add comments regarding the additional data for the current context
            url = url + "/{0}".format(key)
            detail["project"] = project
            payload = self.__prepare_comment(detail=detail)
            response = self.jira_client.put(url, payload)
            if (response.status_code == 204):
                print('Comments were successfully added to the new JIRA.')
            return key
        else:
            print('Failed to create JIRA. Error: {0}'.format(json.loads(response.text)))
            return ""

    def __update_existing(self, issue_key:str, re_open:bool, detail:dict):

        if re_open:
            self.jira_client.change_status(issue_key, 'To Do')

        url = self.jira_client.base_url + "/issue/{0}".format(issue_key)
        payload = self.__prepare_comment(detail=detail)
        response = self.jira_client.put(url, payload)
        if (response.status_code == 204):
            print('JIRA was updated successfully.')
            return issue_key
        else:
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
            return ""

    def __prepare_jira_ticket(self, project, summary:str, description:str, labels:list, affected_version:str):

        ticket = jira_ticket.UemJiraTicket(project_key = project,
                                            issue_type = "Task", 
                                            summary = summary, 
                                            description = description,
                                            priority = { "id": "3" }, # P2
                                            severity = { "id": "13302", "value": "Serious" }, # Severity
                                            component = [{ "name": "Database" }],
                                            labels=labels) 
        # Payload creation
        data = {
            "update": { 
                "description": [{"set": ticket.description}]
                #, "versions": [{"add": { "name": affected_version }}]
            },
            "fields": {
                "summary": ticket.summary,
                "project": ticket.project_key,
                "issuetype": ticket.issue_type,
                "priority": ticket.priority,
                "components": ticket.components, 
                "customfield_12800": ticket.severity,
                "customfield_13000": ticket.defect_phase,
                "customfield_14300": ticket.found_in_automation,
                "labels": ticket.labels
            }
        }

        # if project == "SRE": # SRE project does NOT have affected version field with any values
        #     data["update"].pop("versions")

        payload = json.dumps(data)

        return payload

    def __prepare_comment(self, detail:dict):
        data = {
                "update": {
                    "comment": [
                        { 
                            "add": 
                            { 
                                "body": "Environment: {0}, WS1 Version: {1}, Number of events: {2}"
                                        .format(detail["envt"], detail["version"], detail["count"]) 
                            }
                        }
                    ]
                    #, "versions": [{"add": { "name": detail["affected_version"] }}]
            },
            "fields": {
                "labels": detail["labels"]
            }
        }
        # if detail["project"] == "SRE": # SRE project does NOT have affected version field with any values
        #     data["update"].pop("versions")
        payload = json.dumps(data)
        return payload

