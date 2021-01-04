import json
import traceback
from lib import slack_client
from st2common.runners.base_action import Action

class SlackRemJobResultMessageBuilder(Action):
    def run(self, 
            alert_name=str, 
            alert_url=str, 
            rem_job=str,
            rem_job_results=list,
            targets=list):
        
        client = slack_client.SlackClient(self.config)

        # messages = []

        # Main loop for all results
        # Result is one for each REM job invocation
        for result in rem_job_results:
            rem_job_params = result["params"]
            rem_job_status = int(result["rem_job_number"]) > 0
            result.pop("rem_job_number", -1)
            job_status = ":success:"
            if not rem_job_status:
                job_status = ":fail:"

            # Build the markdown text
            markdown_text = f"*{alert_name}*\nEvent: {alert_url}\nJob: `{rem_job}` {job_status}\n"
            for k, v in rem_job_params.items():
                # if k == "rem_job_number":
                #     continue
                markdown_text += f">{k}: _{v}_\n"

            # Template of the message
            slack_message = {"blocks": []}
            slack_message["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": markdown_text
                    }
                })
            
            # Loop for targets as each job result notification
            # should be sent to all configured slack targets
            for target in targets:
                # notification = {}
                # notification["webhook"] = target
                # notification["body"] = json.dumps(slack_message)
                client.invoke_webhook(target, json.dumps(slack_message))
                # messages.append(notification)

        return True