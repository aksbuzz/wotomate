import requests
import json
from flask import current_app
from ..enums import TriggerType, ActionType
from .template_render import recursive_render

def _execute_http_request(action_config, context_data, workflow_run):
    """
    Placeholder function to execute an HTTP request.
    This function should contain the logic to perform the HTTP request.

    action_config example:
    {
        "url": "https://api.example.com/data",
        "method": "POST", // e.g., GET, POST, PUT, DELETE
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "key": context_data.get("key", ""),
            "value": context_data.get("value", "")
        },
        timeout: 30 // seconds
    }
    """
    current_app.logger.info(f"Executing HTTP_REQUEST for workflow run {workflow_run.id}")
    try:
        rendered_config = recursive_render(action_config, context_data['trigger_data'])
        url = rendered_config.get("url")
        method = rendered_config.get("method", "GET").upper()
        timeout = rendered_config.get("timeout", 30)
        headers = rendered_config.get("headers", {})
        body = rendered_config.get("body", None)
        
        if not url:
            raise ValueError("URL is required for HTTP request")
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        request_kwargs = {"headers": headers, "timeout": timeout}
        
        if method in ["POST", "PUT"]:
            if isinstance(body, dict) or isinstance(body, list):
                # Convert body to JSON if it's a dict or list
                request_kwargs["json"] = body
            elif isinstance(body, str):
                # If body is a string, assume it's already in the correct format
                request_kwargs["data"] = body.encode('utf-8')  # Encode string to bytes if necessary
        
        response = requests.request(method, url, **request_kwargs)  
        response.raise_for_status()  # Raise an error for bad responses
        
        action_result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,  # Use text to get the response body as a string
        }

        try:
            action_result["json"] = response.json()  # Attempt to parse JSON response
        except requests.exceptions.JSONDecodeError:
            pass
        
        workflow_run.action_data = action_result
        workflow_run.log_message = f"HTTP request successful: {response.status_code} {response.reason}"
        current_app.logger.info(f"HTTP request successful for workflow run {workflow_run.id}: {response.status_code} {response.reason}")
        return True
    
    except requests.exceptions.RequestException as e:
        error_message = f"HTTP request failed: {str(e)}"
        current_app.logger.error(error_message)
        workflow_run.log_message = error_message
        if e.response is not None:
            workflow_run.action_data = {
                "error": str(e),
                "status_code": e.response.status_code,
                "body": e.response.text,
            }
        else:
            workflow_run.action_data = {"error": str(e)}
        return False
    
    except ValueError as e:
        error_message = f"Invalid action configuration: {str(e)}"
        current_app.logger.error(error_message)
        workflow_run.log_message = error_message
        workflow_run.action_data = {"error": str(e)}
        return False
    
    except Exception as e:
        error_message = f"Unexpected error during HTTP request: {str(e)}"
        current_app.logger.error(error_message)
        workflow_run.log_message = error_message
        workflow_run.action_data = {"error": str(e)}
        return False


def _log_output(action_config, context_data, workflow_run):
    """
    Placeholder function to log output.
    This function should contain the logic to log the message.

    action_config example:
    {
        "message": "{{trigger.message}} was logged successfully!",
        "level": "info"  # or "debug", "warning", "error", "critical"
    }
    """

    current_app.logger.info(f"Executing LOG_OUTPUT for workflow run {workflow_run.id}")

    try:
        rendered_config = recursive_render(action_config, context_data['trigger_data'])
        message = rendered_config.get("message", "No message provided")
        level = rendered_config.get("level", "info").lower()

        log_function = getattr(current_app.logger, level, current_app.logger.info)
        log_function(f"Workflow Run ID {workflow_run.id}: {message}")

        workflow_run.log_message = f"Logged message: {message[:250]}..."  # Truncate to 250 chars for log
        workflow_run.action_data = {"logged_message": message, "level": level}
        return True
    except Exception as e:
        error_message = f"Error logging output: {str(e)}"
        current_app.logger.error(error_message)
        workflow_run.log_message = error_message
        workflow_run.action_data = {"error": str(e)}
        return False


def _send_email(action_config, context_data, workflow_run):
    """
    Placeholder function to send an email.
    This function should contain the logic to send an email.

    action_config example:
    {
        "subject": "Workflow Notification: context_data.get('workflow_name', 'Untitled!')",
        "body": "Alert! Workflow context_data.get('workflow_name', '') has been triggered.",
        "from": "context_data.get('sender_email', ''),  # or a fixed email address"
        "to": "context_data.get('recipent_email', ''),  # or a fixed email address"
    }
    """
    current_app.logger.info(f"Executing SEND_EMAIL for workflow run {workflow_run.id}")
    
    rendered_config = recursive_render(action_config, context_data['trigger_data'])

    subject = rendered_config.get("subject", "No Subject")
    body = rendered_config.get("body", "No Body")
    recipient = rendered_config.get("to", "")
    sender = rendered_config.get("from", "")

    print(f"Sending email to {recipient} with subject '{subject}' and body '{body}'")  # Replace with actual email sending logic
    return True  # Simulate successful email sending


ACTION_HANDLERS = {
    ActionType.SEND_EMAIL: _send_email,
    ActionType.LOG_OUTPUT: _log_output,
    ActionType.HTTP_REQUEST: _execute_http_request,
}