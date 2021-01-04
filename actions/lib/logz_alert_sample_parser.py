import json

# This class is responsible to extract event samples data from Logz.io Alert 
class LogzAlertSamplesParser:
    # Returns alert data in the generic format for caller automation to use for their respective need
    # Standard template from Logz.io for any custom webhook based endpoint:
    # {
    #     "alert_title": "{{alert_title}}",
    #     "alert_description": "{{alert_description}}",
    #     "alert_severity": "{{alert_severity}}",
    #     "alert_event_samples": "{{alert_samples}}"
    # }
    # which results in...
    # {
    #     "alert_title": "Sprocs with Most Timeouts Detected",
    #     "alert_description": "Link to the Dashboard: https://app.logz.io/#/goto/16e892c206a64ff3f2b369029a18eaa5?switchToAccountId=99208",
    #     "alert_severity": "Medium",
    #     "alert_event_samples": "The following have met the condition: \n[ {\n  \"field1\" : \"field1_value\",\n  \"field2\" : \"field2_value\",\n  \"field3\" : \"field3_value\",\n  \"aggr\" : aggr_value\n } ]"
    # }
    # Removes unnecesary static text and returns samples as they were received
    # Idea is that individual alerts related automation should extrapolate the information provided
    # as they see appropriate. Such automation should NOT be generalized.
    @staticmethod
    def get_samples(event_data:str):
        if event_data:
            samples = json.loads(event_data[event_data.index("[") :].replace("\n", ""))
            return samples
        return []
        