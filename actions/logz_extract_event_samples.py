import json
import traceback
from st2common.runners.base_action import Action

class ExtractLogzAlertEventSamplesAction(Action):

    def run(self, samples:str):
        alert_data = []
        try:
            sources = json.loads(samples[samples.index("[") :].replace("\n", ""))
            alert_data = [source for source in sources]
        except Exception as e:
            self.logger.error("Action failed. {0}".format(str(e)))
            traceback.print_exc()
        return (True, alert_data)