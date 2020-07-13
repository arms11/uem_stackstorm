import sys
import ast

from st2common.runners.base_action import Action

class ParseServiceStateAlertAction(Action):
    def run(self, alertBody):
        failingSources = []
        try:
            print(type(alertBody))
            # Python3 has all strings as Str type and Unicode is not supported.
            if sys.version_info[0] >= 3:
                if isinstance(alertBody, str):
                    data = ast.literal_eval(alertBody)
                    failingSources = data["failingSources"]
            else:
                if isinstance(alertBody, unicode):
                    data = ast.literal_eval(alertBody)
                    failingSources = data["failingSources"]
            return (True, failingSources)
        except Exception as e:
            print('Exception occurred: {ex}'.format(ex=str(e)))
            return (False, failingSources)