from jira import JIRA, Issue as JiraIssue

token = "ATATT3xFfGF0AQ5fOiZGlhaC1t20Od0YsgVy9q0Qo1qxJP74XFYfw-CmH3ug7s7RlyhG1ITHlF-6PZliRsb_h-elIBgRGWsRcYlrUWZQg_m6IKbsLouyRMMm3WU5cIgCMGHmh-Ey2eqIwOHjxgwGDHZjP5xfIAYfDMycYUB4GZznoqhkTZ2_S9I=7A592102"

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
