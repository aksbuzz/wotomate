from project import db
from project.models import ActionDefinition, ConnectorDefinition, TriggerDefinition

def seed():
    github = ConnectorDefinition(
        key="github",
        display_name="GitHub",
        description="Connect your GitHub account to trigger workflows on repository events or perform actions.",
        auth_type="oauth2",
        logo_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
    )
    webhook = ConnectorDefinition(
        key="inbound_webhook",
        display_name="Inbound Webhook",
        description="Trigger workflows when a unique URL receives an HTTP POST request.",
        auth_type="none",
        logo_url="https://your_domain.com/static/images/webhook_icon.png"
    )
    gmail = ConnectorDefinition(
        key="gmail",
        display_name="Gmail",
        description="Connect your Gmail account to send emails or manage your inbox.",
        auth_type="oauth2",
        logo_url="https://your_domain.com/static/images/gmail_icon.png"
    )
    slack = ConnectorDefinition(
        key="slack",
        display_name="Slack",
        description="Connect your Slack workspace to send messages.",
        auth_type="oauth2",
        logo_url="https://your_domain.com/static/images/slack_icon.png"
    )
    db.session.add_all([github, webhook, gmail, slack])
    db.session.commit()

    github_new_issue_trigger = TriggerDefinition(
        connector_definition_id = github.id,
        event_key="new_issue",
        display_name="New Issue",
        description="Triggers when a new issue is created in a selected repository.",
        requires_webhook_endpoint=False,
        config_schema={
            "type": "object",
            "properties": {
                "repository_owner": {"type": "string", "title": "Repository Owner"},
                "repository_name": {"type": "string", "title": "Repository Name"}
            },
            "required": ["repository_owner", "repository_name"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "issue_id": {"type": "integer", "description": "ID of the issue"},
                "issue_number": {"type": "integer", "description": "Number of the issue"},
                "title": {"type": "string", "description": "Title of the issue"},
                "body": {"type": "string", "description": "Body content of the issue"},
                "url": {"type": "string", "format": "uri", "description": "URL of the issue"},
                "user_login": {"type": "string", "description": "Login of the user who created the issue"},
                "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels on the issue"}
            }
        },
    )

    github_new_pr_trigger = TriggerDefinition(
        connector_definition_id = github.id,
        event_key="new_pull_request",
        display_name="New Pull Request Opened",
        description="Triggers when a new pull request is opened or synchronized in a selected repository.",
        requires_webhook_endpoint=False,
        config_schema={
            "type": "object",
            "properties": {
                "repository_owner": {"type": "string", "title": "Repository Owner"},
                "repository_name": {"type": "string", "title": "Repository Name"}
            },
            "required": ["repository_owner", "repository_name"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "pr_id": {"type": "integer", "description": "ID of the pull request"},
                "pr_number": {"type": "integer", "description": "Number of the pull request"},
                "title": {"type": "string", "description": "Title of the pull request"},
                "body": {"type": "string", "description": "Body content of the pull request"},
                "url": {"type": "string", "format": "uri", "description": "URL of the pull request"},
                "user_login": {"type": "string", "description": "Login of the user who opened the PR"},
                "state": {"type": "string", "description": "State (e.g., open, closed)"},
                "source_branch": {"type": "string"},
                "target_branch": {"type": "string"}
            }
        },
    )

    webhook_trigger = TriggerDefinition(
        connector_definition_id=webhook.id,
        event_key="http_request_received",
        display_name="Webhook Called",
        description="Triggers when the workflow's unique webhook URL is called.",
        config_schema={
            "type": "object",
            "properties": {
                "expected_payload_schema": {
                    "type": "object",
                    "title": "Expected Payload JSON Schema (Optional)",
                    "description": "Define a JSON schema to validate incoming webhook payloads and provide typed outputs."
                }
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "body": {"type": ["object", "array", "string", "number", "boolean", "null"], "description": "Parsed JSON body or raw body if not JSON"},
                "headers": {"type": "object", "description": "Request headers"},
                "query_params": {"type": "object", "description": "URL query parameters"},
                "method": {"type": "string", "description": "HTTP method (e.g., POST, GET)"}
            }
        },
        requires_webhook_endpoint=True
    )
    db.session.add_all([github_new_issue_trigger, github_new_pr_trigger, webhook_trigger])
    db.session.commit()

    gmail_send_email_action = ActionDefinition(
        connector_definition_id=gmail.id,
        action_key="send_email",
        display_name="Send an Email",
        description="Sends an email using the connected Gmail account.",
        config_schema={
            "type": "object",
            "properties": {
                "to_address": {"type": "string", "format": "email", "title": "To"},
                "cc_address": {"type": "string", "format": "email", "title": "CC (Optional)"},
                "bcc_address": {"type": "string", "format": "email", "title": "BCC (Optional)"},
                "subject": {"type": "string", "title": "Subject"},
                "body_html": {"type": "string", "title": "Body (HTML)", "format": "textarea"},
                "body_text": {"type": "string", "title": "Body (Plain Text - Optional)", "format": "textarea"}
            },
            "required": ["to_address", "subject"]
        },
        input_schema={
            "type": "object",
            "properties": {
                "to_address": {"type": "string"},
                "cc_address": {"type": "string"},
                "bcc_address": {"type": "string"},
                "subject": {"type": "string"},
                "body_html": {"type": "string"},
                "body_text": {"type": "string"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "ID of the sent email"},
                "status": {"type": "string", "enum": ["sent", "failed"], "description": "Sending status"}
            }
        }
    )
    slack_send_message_action = ActionDefinition(
        connector_definition_id=slack.id,
        action_key="send_channel_message",
        display_name="Send Message to Channel",
        description="Posts a message to a specified Slack channel.",
        config_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "title": "Channel ID (e.g., C1234567890) or Name (e.g., #general)"},
                "message_text": {"type": "string", "title": "Message Text", "format": "textarea"},
                "as_user": {"type": "boolean", "title": "Send as authenticated user (bot default)", "default": False}
            },
            "required": ["channel_id", "message_text"]
        },
        input_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "message_text": {"type": "string"},
                "as_user": {"type": "boolean"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "message_ts": {"type": "string", "description": "Timestamp of the sent message"},
                "channel_id": {"type": "string", "description": "ID of the channel where message was sent"},
                "status": {"type": "string", "enum": ["sent", "failed"]}
            }
        }
    )
    db.session.add_all([gmail_send_email_action, slack_send_message_action])
    db.session.commit()

def run_all():
    seed()
    print("Seeded connectors, triggers, and actions.")

if __name__ == "__main__":
    run_all()
