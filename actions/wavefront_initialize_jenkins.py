from st2common.runners.base_action import Action

class WavefrontAlertToJenkinsMapperAction(Action):
    # def run(self, jenkins_metadata:dict, source_data:dict):
    def run(self, jenkins_metadata:dict, sources:list):
        job_payloads = []
        for source_data in sources:
            print(str(source_data))
            job_payload = {}
            try:
                # Transform templated data using the source data
                for k, v in jenkins_metadata["params"].items():
                    if v.startswith("{") and v.endswith("}"):
                        point_tag = v.replace("{", "").replace("}", "")
                        print(point_tag)
                        job_payload[k] = source_data[point_tag]
                    else:
                        job_payload[k] = v # regular value to be left alone
                
                # We get values like 'US02PRDSQL271A:SQL271A' which causes client exception and not needed.
                # This method should help remove unnecessary portion to avoid such issue.
                if jenkins_metadata["project"].lower() == "sql_free_systemcache":
                    job_payload["SqlServer"] = WavefrontAlertToJenkinsMapperAction.get_sql_instance(source_data["sql_instance"])
                
                job_payloads.append(job_payload)
            except Exception as e:
                self.logger.error("Failed to map data. {0}".format(str(e)))
        return (True, job_payloads)
    
    @staticmethod
    def get_sql_instance(sql_instance):
        if sql_instance is None:
            sql_instance = ""
        elif sql_instance.strip() and sql_instance.find(":") != -1:
            sql_instance = sql_instance.split(":")[0]
        return sql_instance