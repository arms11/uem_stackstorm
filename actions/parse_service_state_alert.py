import sys
import ast

from st2common.runners.base_action import Action

class ParseServiceStateAlertAction(Action):
    def run(self, alertBody):
        try:
            if isinstance(alertBody, unicode):
                data = ast.literal_eval(alertBody)
                print(data["failingSources"])
                return (True, data["failingSources"])
            else:
                print(type(alertBody))
                return (True, ["Not able to parse"])
        except Exception as e:
            return (False, 'Exception occurred: {ex}'.format(ex=str(e)))
        