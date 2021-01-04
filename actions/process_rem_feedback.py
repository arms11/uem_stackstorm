import traceback

from lib import pagerduty_client
from st2common.runners.base_action import Action

class ProcessRemFeedback(Action):
    def run(self, 
            pd_target:str, 
            response_code:str, 
            response_message:str, 
            client_url:str, 
            job_params:list):
        pdClient = pagerduty_client.PagerDutyClient(self.config)
        rem_instance_url = self.config["jenkins_url"]
        
        # Send PagerDuty Notification to Create an Incident
        try:
            routing_key = pd_target
            custom_details = {}
            if len(job_params) > 0:
                custom_details = job_params[0]
            custom_details["response_code"] = response_code
            custom_details["response_message"] = response_message
            if client_url.find(",") != -1:
                client_url = client_url.split(",")[0]
            summary = "REM failure alert"
            if "rem_alert_name" in custom_details:
                summary = "REM failure: {0}".format(custom_details["rem_alert_name"])
            pdClient.post_event(routing_key=routing_key,
                                summary=summary,
                                source=rem_instance_url,
                                custom_details=custom_details,
                                client_url=client_url)
        except Exception as e:
            self.logger.error("Action failed. {0}".format(str(e)))
            traceback.print_exc()
            return False
        return True