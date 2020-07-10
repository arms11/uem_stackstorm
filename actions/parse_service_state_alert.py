import sys
import ast

from st2common.runners.base_action import Action

class ParseServiceStateAlertAction(Action):
    def run(self, alertBody):
        failingSources = []
        try:
            if isinstance(alertBody, unicode):
                data = ast.literal_eval(alertBody)
                failingSources = data["failingSources"]
                print(failingSources)
                return (True, failingSources)
            else:
                print(type(alertBody))
                return (True, failingSources)
        except Exception as e:
            print('Exception occurred: {ex}'.format(ex=str(e)))
            return (False, failingSources)
        