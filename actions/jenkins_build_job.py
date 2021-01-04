import traceback

from lib import jenkins_client
from st2common.runners.base_action import Action

class JenkinsBuildJobInvoker(Action):

    # Main method that kicks off the job by invoking Jenkins Build_Job method
    # def run(self, project:str, params:dict):
    def run(self, project:str, job_params_list:list):
        job_results = []
        for params in job_params_list:
            job_result = {}
            job_no = -1
            job_result["rem_job_number"] = job_no
            job_result["params"] = params.copy()
            try:
                jenkinsClient = jenkins_client.JenkinsClient(self.config)
                job_no = jenkinsClient.run_job(project, params=params)
            except Exception as e:
                self.logger.error("Action failed. {0}".format(str(e)))
                #traceback.print_exc()
            finally:
                job_result["rem_job_number"]=job_no
                job_results.append(job_result)
        return job_results