import json
from st2common.runners.base_action import Action
from lib import logz_alert_parser

class ParseSprocTimeoutsAlertAction(Action):

    def run(self, alertBody):
        alert_data = {}
        try:
            print(type(alertBody))
            alert_data["title"] = alertBody["alert_title"]
            alert_data["description"] = alertBody["alert_description"]
            alert_data["severity"] = alertBody["alert_severity"]
            alert_data["detail"] = self.__extract_detail(alertBody["alert_event_samples"])
            return (True, alert_data)
        except Exception as e:
            print('Exception occurred: {ex}'.format(ex=str(e)))
            return (False, alert_data)
        
    def __extract_detail(self, alert_event_samples):
        samples = json.loads(alert_event_samples[alert_event_samples.index("[") :].replace("\n", ""))
        environments = []
        for sample in samples:
            environment = {
                "environment" : sample["fields.env_name"],
                "version" : "", ##############TODO: Current Alert definition needs to incorporate this #sample["fields.ws1_release"],
                "sproc" : sample["StoredProcedureName"],
                "count": sample["count"]
            }
            environments.append(environment)
        return environments