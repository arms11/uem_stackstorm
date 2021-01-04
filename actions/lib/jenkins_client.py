import jenkins

# Utility class for Jenkins Interaction
class JenkinsClient:

    def __init__(self, actionConfig):
        self.api_token = actionConfig['jenkins_api_token']
        self.jenkins = self._get_client(actionConfig)

    def _get_client(self, config):
        url = config['jenkins_url']
        try:
            username = config['jenkins_username']
        except KeyError:
            username = None
        try:
            password = config['jenkins_password']
        except KeyError:
            password = None

        client = jenkins.Jenkins(url, username, password)
        client._session.verify = False # suppress SSL verification
        return client
    
    def run_job(self, project, params=None):
        return self.jenkins.build_job(name=project, parameters=params, token=self.api_token)
        
