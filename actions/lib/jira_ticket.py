# Generic class for JIRA ticket of IssueType = Bug
# Below fields are all required for any UEM JIRA Project
class UemJiraTicket:
    def __init__(self, project_key:str, issue_type:str, summary:str, description:str, priority:dict, severity:dict, components:list, labels:list):
        self.project_key = { "key": project_key }
        self.summary = summary
        self.description = description
        self.priority = priority
        self.severity = severity
        self.issue_type = { "name": issue_type } # Bug or Task
        self.labels = labels 
        self.found_in_automation = { "id": "15407", "value": "No" }
        self.defect_phase = { "id": "16200", "value": "SRE Identified" }
        self.components = components