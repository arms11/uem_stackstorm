import sys

from st2common.runners.base_action import Action

class ParseServiceStateAlertAction(Action):
    def run(self, alertBody):
        try:
            print(alertBody)
            
            if isinstance(alertBody, dict):
                return (True, "alertBody is a dictionary")
            elif isinstance(alertBody, list):
                return (True, "alertBody is a list")
            elif isinstance(alertBody, str):
                return (True, "alertBody is a string")
            else:
                print(type(alertBody))
                return (True, "Unknown type")
        except Exception as e:
            return (False, 'Exception occurred: {ex}'.format(ex=str(e)))
        