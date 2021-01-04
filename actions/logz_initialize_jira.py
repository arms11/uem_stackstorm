import traceback
from st2common.runners.base_action import Action
from lib import jira_client

class LogzAlertToJiraMapperAction(Action):
    def run(self, 
            alert_name:str, 
            alert_description:str, 
            alert_severity:str,
            metadata:dict, 
            source:dict):
        jira_ticket = {}
        self.source = source
        self.source["alert_name"] = alert_name
        self.source["alert_severity"] = alert_severity
        self.source["alert_description"] = alert_description
        try:
            tranformed_data = self.__get_transformed_values(metadata["summary"], metadata["labels"])
            jira_ticket["project"] = metadata["project"]
            jira_ticket["type"] = metadata["issue-type"]
            jira_ticket["summary"] = tranformed_data["summary"]
            jira_ticket["description"] = tranformed_data["description"]
            jira_ticket["custom_fields"] = {
              "priority": self.__get_priority(),
              "severity": self.__get_severity(),
              "components": self.__get_components(metadata["components"]),
              "labels": tranformed_data["labels"],
              "affected_version": self.__get_affected_version()
            }
            return (True, jira_ticket)
        except Exception as e:
            self.logger.error("Failed to map data. {0}".format(str(e)))
            traceback.print_exc()
            return (False, jira_ticket)
    
    def __get_transformed_values(self, summary_metadata:str, labels_metadata:str):
      summary = summary_metadata
      description = ""
      labels_str = labels_metadata
      for k,v in self.source.items():
        summary = summary.replace("{" + k + "}", str(v))
        labels_str = labels_str.replace("{" + k + "}", str(v))
        description += k + " = " + str(v) + "\n"
      return {
        "summary": summary,
        "description": description,
        "labels": labels_str.split(",")
      }

    def __get_severity(self):
      # Not sure if Catastrophic makes sense!
      # But in case...{ "id": "13300", "value": "Catastrophic" }
      if self.source["alert_severity"].upper() == "SEVERE" or self.source["alert_severity"].upper() == "HIGH":
        return { "id": "13301", "value": "Critical" }
      return { "id": "13302", "value": "Serious" }

    def __get_priority(self):
      # Not sure if P0 makes sense!
      # But in case...{ "id": "1", "name": "P0" }
      if self.source["alert_severity"].upper() == "SEVERE" or self.source["alert_severity"].upper() == "HIGH":
        return { "id": "2", "name": "P1" }
      return { "id": "3", "name": "P2" }

    def __get_components(self, components_metadata:str):
      components = []
      for component in components_metadata.strip().split(","):
        components.append({ "name" : component })
      return components

    def __get_affected_version(self):
      if "fields.ws1_release" in self.source:
        return jira_client.JiraClient.derive_affected_version(self.source["fields.ws1_release"])
      return "Future"