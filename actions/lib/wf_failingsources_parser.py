import traceback

# This class is responsible to extract data from failingAlertSeries used 
# in generic Alert template in Wavefront to Dictionary for ease of use
# by automation workflows
class WavefrontFailingSourcesParser:
    def __init__(self, alertBody:dict):
        self.data = alertBody

    def get_failing_sources(self):
        failingSources = []
        try:
            sources = self.data["failingSources"]
            for source in sources:
                failingSource = {}
                failingSource["host"] = source["host"]
                tags = self.to_dictionary(source["tags"])
                for key, value in tags.items():
                    failingSource[key] = value
                failingSources.append(failingSource)           
        except Exception as e:
            print('Parsing Exception occurred: {ex}'.format(ex=str(e)))
            traceback.print_exc()
        return failingSources
    
    # Wavefront alerts have a predefined format in their 'failingAlertSeries' where the 
    # point-tags will be returned in comma-separated 'key=value' format.
    # ********************** Sample Data *****************************
    # "{environment&#61;CN118, instance&#61;us04pcn118ba\\private$\\apnsoutbound, ws1version&#61;20.8.0.6, hosttype&#61;CN, 
    #  databasename&#61;AirWatch_DB118, objectname&#61;MSMQ Queue, datacenter&#61;US04, deployment&#61;production}"
    # ****************************************************************
    # This method will extract this data and will return a qulified dictionary as output.
    def to_dictionary(self, tags:str):
        result = {}
        if tags:
            point_tags = tags.replace("{", "").replace("}", "").replace("&#61;", "=").split(",")
            for pt in point_tags:
                pair = pt.strip().split("=")
                result[pair[0]] = pair[1]
        return result