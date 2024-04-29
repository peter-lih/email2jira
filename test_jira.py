from jira import JIRA, Issue as JiraIssue

if __name__ == "__main__":
    options = {
        "server": "",
        "verify": False,
    }  # Disable certificate verification
    jira = JIRA(options=options, basic_auth=("", ""))

    issue_dict = {
        "project": {"key": "test"},  # Replace with the actual project key
        "summary": "testing",
        "issuetype": {"name": "Task"},
    }

    jira_ticket = jira.create_issue(fields=issue_dict)
    print(jira_ticket)
