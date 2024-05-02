from jira import JIRA, Issue as JiraIssue

token = ""

if __name__ == "__main__":
    options = {
        "server": "https://liyao.atlassian.net",
        "verify": False,
    }  # Disable certificate verification
    jira = JIRA(options=options, basic_auth=("peter@liyao.co", token))

    issue_dict = {
        "project": {"key": "TEST"},  # Replace with the actual project key
        "summary": "testing4",
        "issuetype": {"name": "Task"},
        "priority": {"name": "Medium"},
        "labels": ["test"],
        "assignee": {"id": "712020:d8e360ce-67af-465b-a2fd-b048dc6f3107"},
        "duedate": "2024-12-31T00:00:00.000+0000",
    }

    # jira_ticket = jira.issue("TEST-1")
    jira_ticket = jira.create_issue(fields=issue_dict)
    print(jira_ticket.fields.__dict__)
