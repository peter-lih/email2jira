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
        "summary": "testingw",
        "issuetype": {"name": "Task"},
        "labels": ["test"],
    }

    jira_ticket = jira.create_issue(fields=issue_dict)
    print(jira_ticket)
