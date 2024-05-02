import imaplib
from email.parser import BytesParser
from email.message import Message
from email.header import decode_header
from jira import JIRA
import requests
import html2text
import yaml
import os

requests.packages.urllib3.disable_warnings()


def get_cconfig() -> dict:
    """
    Setup configuration
    """

    path = "./config.yaml"
    if os.path.exists(path):
        with open(path, "rt", encoding="utf8") as f:
            cfg = yaml.safe_load(f.read())
        return cfg
    else:
        print(f"Config file not found: {path}")
        return {}


def parse_plain_table(body: str) -> dict:
    """Parse plain text table to dictionary. The table content is between `---|---` and 'end  |'.
    plain text table format:
        ```
        Some text here

        field |  content
        ---|---
        A  |  B
        C  |  D
        multi-line
        end  |

        more text here
        ```

    Args:
        body: email content

    Returns:
        Dictionary of field and content.
    """
    resultd = {}
    _key, _value = "", ""
    _start = False
    lines = body.strip().splitlines()
    for i in range(len(lines)):
        # start of the table
        if "---|---" in lines[i]:
            _start = True
            continue

        # end of the table
        if "end" in lines[i] and "|" in lines[i]:
            _start = False
            break

        if not _start:
            continue

        parsed = lines[i].strip().split("|")
        if len(parsed) != 2:
            resultd[_key] += "\n " + parsed[0].strip()
        else:
            _key, _value = parsed
            _key = _key.strip()
            _value = _value.strip()
            resultd[_key] = _value

    return resultd


# Function to convert HTML to plaintext
def html_to_plaintext(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    return h.handle(html_content)


def get_subject(msg: Message) -> str:
    """Pase email subject

    Args:
        msg: Email message

    Returns:
        str: Parsed email subject
    """
    headers = decode_header(msg["Subject"])
    subject = None
    for header in headers:
        decoded_header = header[0]
        if header[1]:
            charset = header[1]
            # Decode the subject using the specified charset
            if charset:
                decoded_header = decoded_header.decode(charset)
        subject = decoded_header
    return str(subject)


def get_body(msg: Message) -> str:
    """Parse email body

    Args:
        msg: Email message

    Returns:
        str: Parsed email body
    """
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == "text/plain":
            return part.get_payload(decode=True).decode("utf-8")
        elif content_type == "text/html":
            html_body = part.get_payload(decode=True).decode("utf-8")
            return html_to_plaintext(html_body)

    return ""


if __name__ == "__main__":
    cfg = get_cconfig()
    print("Get config")

    options = {
        "server": cfg.get("JIRA_URL"),
        "verify": False,
    }  # Disable certificate verification
    # Connect to IMAP server
    print("Connecting to IMAP server...")
    imap_server = imaplib.IMAP4_SSL(cfg.get("IMAP_SERVER", ""))
    imap_server.login(cfg.get("IMAP_USERNAME", ""), cfg.get("IMAP_PASSWORD", ""))
    print("Connected to IMAP server.")

    # Select the mailbox to monitor
    print(f"Selecting mailbox: {cfg.get('INBOX_PATH', '')}")
    imap_server.select(cfg.get("INBOX_PATH", ""))
    print(f"Selected mailbox: {cfg.get('INBOX_PATH', '')}")

    # Connect to Jira using the API URL
    print("Connecting to Jira...")
    jira = JIRA(
        options=options,
        basic_auth=(cfg.get("JIRA_USERNAME", ""), cfg.get("JIRA_PASSWORD", "")),
    )
    print("Connected to Jira.")
    # Search for all emails in the mailbox
    print("Searching for emails...")
    status, messages = imap_server.search(None, "ALL")

    if status == "OK":
        print(f"Found {len(messages[0].split())} email(s).")
        for num in messages[0].split():
            _, msg_data = imap_server.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = BytesParser().parsebytes(response_part[1])

                    # Parse email headers
                    subject = get_subject(msg)
                    if not cfg.get("JIRA_PROJECT_KEY") in subject:
                        continue

                    # Parse email body if needed
                    body = get_body(msg)

                    # Create Jira ticket
                    print("Processing email...")
                    issue_dict = {
                        "project": {
                            "key": cfg.get("JIRA_PROJECT_KEY")
                        },  # Replace with the actual project key
                        "summary": subject,
                        "issuetype": {"name": "Task"},
                    }
                    text2jira = cfg.get("TEXT2JIRA", {})
                    emaild = parse_plain_table(body)
                    for _field, _content in emaild.items():
                        if _field not in text2jira.keys():
                            continue

                        # `labels` field is a list
                        issue_field = text2jira[_field]["FIELD"]
                        if issue_field == "labels":
                            if _content:
                                issue_dict[issue_field] = [_content]
                            else:
                                issue_dict[issue_field] = [
                                    text2jira[_field].get("DEFAULT", "")
                                ]

                        else:
                            if _content:
                                issue_dict[issue_field] = _content
                            else:
                                issue_dict[issue_field] = text2jira[_field].get(
                                    "DEFAULT", ""
                                )

                    jira_ticket = jira.create_issue(fields=issue_dict)
                    print(f"Jira ticket created: {jira_ticket.key}")

                    # Move the email to the completed mailbox
                    print(f"Moving email to {cfg.get('COMPLETED_PATH', '')}...")
                    imap_server.copy(num, cfg.get("COMPLETED_PATH", ""))
                    imap_server.store(num, "+FLAGS", "\\Deleted")
                    print("Email moved to the completed mailbox.")

    # Permanently remove deleted emails and logout from IMAP server
    print("Cleaning up...")
    imap_server.expunge()
    print("Cleanup completed.")
    imap_server.logout()

    print("Done.")
