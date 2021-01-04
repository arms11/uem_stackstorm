import traceback
from st2common.runners.base_action import Action
from lib import wf_failingsources_parser

class ParseInstanceAlertAction(Action):
    def run(self, alertBody):
        failingSources = []
        try:
            parser = wf_failingsources_parser.WavefrontFailingSourcesParser(alertBody)
            failingSources = parser.get_failing_sources()          
            return (True, failingSources)
        except Exception as e:
            self.logger.error("Parse Instance Action failed. {0}".format(str(e)))
            traceback.print_exc()
            return (False, failingSources)