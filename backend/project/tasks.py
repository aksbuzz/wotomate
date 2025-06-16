from project.services.template_render import resolve_template
from project.models import Trigger, Workflow, WorkflowRun, WorkflowRunAction, Connector
from project import create_app, db
from flask import current_app
from datetime import datetime
from celery.exceptions import MaxRetriesExceededError
from . import celery_app
from project.utils import decrypt_value
import requests


@celery_app.task(name='project.tasks.poll_all_triggers_task', bind=True)
def poll_all_triggers_task(self):
    with create_app().app_context():
        session = db.session
        try:
            now = datetime.utcnow()
            current_app.logger.info(f"[{now.isoformat()}] Running poll_all_triggers_task...")

            # TODO: Onyl published workflows ??
            due_triggers = session.query(Trigger).\
                join(Workflow, Trigger.workflow_id == Workflow.id).\
                filter(Workflow.is_active == True).\
                filter(Trigger.webhook_id == None)
            
            triggers_to_poll_now = [t for t in due_triggers if t.should_poll()]
            current_app.logger.info(f"Found {len(triggers_to_poll_now)} triggers due for polling.")

            for trigger_instance in triggers_to_poll_now:
                poll_single_trigger_task.delay(trigger_instance.id)

            # session.commit()
        except Exception as e:
            current_app.logger.error(f"Error in poll_all_triggers_task: {e}")
            session.rollback()


@celery_app.task(name='project.tasks.poll_single_trigger_task', bind=True, max_retries=3, default_retry_delay=60)
def poll_single_trigger_task(self, trigger_id: int):
    with create_app().app_context():
        session = db.session
        try:
            # TODO: use joinedload
            trigger_instance = Trigger.query.get(trigger_id)
            if not trigger_instance or not trigger_instance.workflow.is_active:
                current_app.logger.error(f"Trigger ID {trigger_id} no longer valid for polling. Skipping.")
                return

            current_app.logger.info(f"Polling trigger ID: {trigger_id} for workflow: {trigger_instance.workflow.name}")

            connector_key = trigger_instance.trigger_definition.connector_definition.key
            event_key = trigger_instance.trigger_definition.event_key
            new_events_data = []

            # GITHUB NEW ISSUE
            if connector_key == "github" and event_key == "new_issue":
                owner = trigger_instance.config.get("repository_owner")
                repo_name = trigger_instance.config.get("repository_name")

                if not owner or not repo_name:
                    current_app.logger.error(f"Missing config for GitHub trigger {trigger_id}. Skipping.")
                    trigger_instance.last_polled_at = datetime.utcnow() # Mark as polled to avoid immediate re-poll
                    session.commit()
                    return

                connector = Connector.query.get(trigger_instance.connector_id)
                if not connector or not connector.credentials.get('access_token'):
                    current_app.logger.error(f"Missing GitHub credentials for trigger {trigger_id}. Skipping.")
                    trigger_instance.last_polled_at = datetime.utcnow()
                    session.commit()
                    return

                access_token = decrypt_value(connector.credentials.get('access_token'))
                issues_headers = {
                    'Authorization': f"Bearer {access_token}",
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
                issues_params = {'state': 'open', 'sort': 'created', 'direction': 'asc', 'per_page': 30}
                last_seen_timestamp_iso = (trigger_instance.polling_state or {}).get("last_seen_issue_created_at")
                if last_seen_timestamp_iso:
                    issues_params['since'] = last_seen_timestamp_iso
                
                try:
                    api_url = f'https://api.github.com/repos/{owner}/{repo_name}/issues'
                    current_app.logger.debug(f"Fetching GitHub issues: URL={api_url}, Params={issues_params}")
                    issues_response = requests.get(api_url, headers=issues_headers, params=issues_params, timeout=15)
                    issues_response.raise_for_status()
                    issues = issues_response.json()
                    current_app.logger.debug(f"GitHub API response for trigger {trigger_id}: {len(issues)} issues received.")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        current_app.logger.error(f"GitHub API returned 401 Unauthorized for trigger {trigger_id}. Token might be invalid or revoked. Skipping.")
                        # TODO: notify the user
                    elif e.response.status_code == 403:
                        current_app.logger.warning(f"GitHub API returned 403 Forbidden for trigger {trigger_id}. Check scopes or rate limits. Error: {e.response.text}")
                    elif e.response.status_code == 404:
                        current_app.logger.error(f"GitHub repo {owner}/{repo_name} not found for trigger {trigger_id}. Skipping.")
                    else:
                        current_app.logger.error(f"HTTP error fetching GitHub issues for trigger {trigger_id}: {e}. Response: {e.response.text}")
                    
                    trigger_instance.last_polled_at = datetime.utcnow() # Mark as polled to avoid immediate retry on error
                    session.commit()
                    return
                except requests.exceptions.RequestException as e:
                    current_app.logger.error(f"Network error fetching GitHub issues for trigger {trigger_id}: {e}. Will retry.")
                    raise self.retry(exc=e)
                
                latest_issue_created_at_iso = last_seen_timestamp_iso
                new_issue_count = 0
                for issue in issues:
                    issue_created_at = issue.get("created_at")
                    if not issue_created_at:
                        continue

                    # GitHub's 'since' param is inclusive, so skip issues with created_at == last_seen_timestamp_iso
                    if last_seen_timestamp_iso and issue_created_at <= last_seen_timestamp_iso:
                        continue
                    
                    new_issue_count += 1
                    event_data = {
                        "issue_id": issue.get("id"),
                        "issue_number": issue.get("number"),
                        "title": issue.get("title"),
                        "body": issue.get("body"),
                        "url": issue.get("html_url"),
                        "user_login": issue.get("user", {}).get("login"),
                        "labels": [label.get("name") for label in issue.get("labels", [])],
                        "repository_name": repo_name,
                        "_event_timestamp_utc": issue.get("created_at") # For state management
                    }
                    new_events_data.append(event_data)

                    # Track the latest created_at for next poll
                    if not latest_issue_created_at_iso or issue_created_at > latest_issue_created_at_iso:
                        latest_issue_created_at_iso = issue_created_at

                if new_issue_count > 0:
                    current_app.logger.info(f"Trigger {trigger_id}: Found {new_issue_count} new GitHub issues since {last_seen_timestamp_iso or 'the beginning'}.")
                
                # Update polling state
                if latest_issue_created_at_iso: # Only update if we have a valid timestamp
                    trigger_instance.polling_state = {"last_seen_issue_created_at": latest_issue_created_at_iso}
                current_app.logger.info(f"Found {len(new_events_data)} new GitHub issues. New polling state: {trigger_instance.polling_state}")

            # GITHUB NEW ISSUE END

            # GITHUB NEW PULL REQUEST
            elif connector_key == "github" and event_key == "new_pull_request":
                owner = trigger_instance.config.get("repository_owner")
                repo_name = trigger_instance.config.get("repository_name")

                if not owner or not repo_name:
                    current_app.logger.error(f"Missing config for GitHub trigger {trigger_id}. Skipping.")
                    trigger_instance.last_polled_at = datetime.utcnow() # Mark as polled to avoid immediate re-poll
                    session.commit()
                    return

                connector = Connector.query.get(trigger_instance.connector_id)
                if not connector or not connector.credentials.get('access_token'):
                    current_app.logger.error(f"Missing GitHub credentials for trigger {trigger_id}. Skipping.")
                    trigger_instance.last_polled_at = datetime.utcnow()
                    session.commit()
                    return

                access_token = decrypt_value(connector.credentials.get('access_token'))
                pr_headers = {
                    'Authorization': f"Bearer {access_token}",
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
                pr_params = {'state': 'open', 'sort': 'created', 'direction': 'asc', 'per_page': 30}
                last_seen_timestamp_iso = (trigger_instance.polling_state or {}).get("last_seen_pr_created_at")
                if last_seen_timestamp_iso:
                    pr_params['since'] = last_seen_timestamp_iso

                try:
                    api_url = f'https://api.github.com/repos/{owner}/{repo_name}/pulls'
                    current_app.logger.debug(f"Fetching GitHub PRs: URL={api_url}, Params={pr_params}")
                    pr_response = requests.get(api_url, headers=pr_headers, params=pr_params, timeout=15)
                    pr_response.raise_for_status()
                    prs = pr_response.json()
                    current_app.logger.debug(f"GitHub API response for trigger {trigger_id}: {len(prs)} PRs received.")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        current_app.logger.error(f"GitHub API returned 401 Unauthorized for trigger {trigger_id}. Token might be invalid or revoked. Skipping.")
                        # TODO: notify the user
                    elif e.response.status_code == 403:
                        current_app.logger.warning(f"GitHub API returned 403 Forbidden for trigger {trigger_id}. Check scopes or rate limits. Error: {e.response.text}")
                    elif e.response.status_code == 404:
                        current_app.logger.error(f"GitHub repo {owner}/{repo_name} not found for trigger {trigger_id}. Skipping.")
                    else:
                        current_app.logger.error(f"HTTP error fetching GitHub PRs for trigger {trigger_id}: {e}. Response: {e.response.text}")
                    
                    trigger_instance.last_polled_at = datetime.utcnow() # Mark as polled to avoid immediate retry on error
                    session.commit()
                    return
                except requests.exceptions.RequestException as e:
                    current_app.logger.error(f"Network error fetching GitHub PRs for trigger {trigger_id}: {e}. Will retry.")
                    raise self.retry(exc=e)

                latest_pr_created_at_iso = last_seen_timestamp_iso
                new_pr_count = 0
                for pr in prs:
                    pr_created_at = pr.get("created_at")
                    if not pr_created_at:
                        continue

                    # GitHub's 'since' param is inclusive, so skip prs with created_at == last_seen_timestamp_iso
                    if last_seen_timestamp_iso and pr_created_at <= last_seen_timestamp_iso:
                        continue
                    
                    new_pr_count += 1
                    event_data = {
                        "pr_id": pr.get("id"),
                        "pr_number": pr.get("number"),
                        "title": pr.get("title"),
                        "body": pr.get("body"),
                        "url": pr.get("html_url"),
                        "user_login": pr.get("user", {}).get("login"),
                        "state": pr.get("state"),
                        "source_branch": pr.get("head", {}).get("ref"),
                        "target_branch": pr.get("base", {}).get("ref"),
                        "_event_timestamp_utc": pr.get("created_at") # For state management
                    }
                    new_events_data.append(event_data)

                    # Track the latest created_at for next poll
                    if not latest_pr_created_at_iso or pr_created_at > latest_pr_created_at_iso:
                        latest_pr_created_at_iso = pr_created_at

                if new_pr_count > 0:
                    current_app.logger.info(f"Trigger {trigger_id}: Found {new_pr_count} new GitHub PRs since {last_seen_timestamp_iso or 'the beginning'}.")
                
                # Update polling state
                if latest_pr_created_at_iso: # Only update if we have a valid timestamp
                    trigger_instance.polling_state = {"last_seen_pr_created_at": latest_pr_created_at_iso}
                current_app.logger.info(f"Found {len(new_events_data)} new GitHub PRs. New polling state: {trigger_instance.polling_state}")

            # GITHUB NEW PULL REQUEST END

            if new_events_data:
                current_app.logger.info(f"Trigger {trigger_id} produced {len(new_events_data)} new events. Dispatching workflow executions.")
                for event_data in new_events_data:
                    processed_event_data = {k:v for k,v in event_data.items() if not k.startswith('_')}
                    execute_workflow_task.delay(trigger_instance.workflow_id, processed_event_data)
                    current_app.logger.info(f"Dispatched workflow execution for workflow ID {trigger_instance.workflow_id} with event: {event_data.get('title', event_data.get('id'))}")
            else:
                current_app.logger.info(f"Trigger {trigger_id}: No new events found this poll.")
            
            trigger_instance.last_polled_at = datetime.utcnow()
            session.commit()

        except Exception as e:
            current_app.logger.error(f"Error polling trigger ID {trigger_id}: {e}")
            session.rollback()
            try:
                raise self.retry(exc=e)
            except MaxRetriesExceededError:
                current_app.logger.error(f"Max retries exceeded for polling trigger ID {trigger_id}. Giving up on this poll attempt.")


@celery_app.task(name='project.tasks.execute_workflow_task', bind=True, max_retries=3, default_retry_delay=300)
def execute_workflow_task(self, workflow_id: int, trigger_event_data: dict):
    with create_app().app_context():
        session = db.session
        current_run = None #
        overall_run_status = "running"
        
        try:
            workflow_to_run = Workflow.query.get(workflow_id)

            if not workflow_to_run or not workflow_to_run.is_active:
                current_app.logger.error(f"Workflow {workflow_id} not found or inactive for execution. Skipping.")
                return
            
            current_app.logger.info(f"Executing workflow: {workflow_to_run.name} (ID: {workflow_id}) for trigger event: {trigger_event_data.get('title', 'N/A')}")
            
            template_context = {
                "trigger": { "output": trigger_event_data },
                "actions": {}
            }
            
            current_run = WorkflowRun(
                workflow_id=workflow_to_run.id,
                workflow=workflow_to_run,
                status='running',
                trigger_event_data=trigger_event_data,
            )

            session.add(current_run)
            session.flush()
            current_app.logger.info(f"Workflow Run ID: {current_run.id} started for Workflow ID: {workflow_to_run.id}")

            actions_to_execute = sorted(workflow_to_run.actions, key=lambda a: a.position)

            for action_config in actions_to_execute:
                run_action_log_messages = []
                run_action_status = "running"
                run_action_input_data_for_log = {}
                run_action_output_data = None
                action_start_time = datetime.utcnow()

                run_action = WorkflowRunAction(
                    run_id=current_run.id,
                    action_id=action_config.id,
                    position=action_config.position,
                    status=run_action_status,
                    started_at=action_start_time
                )
                session.add(run_action)
                session.flush()

                try:
                    action_def = action_config.action_definition
                    connector_def = action_def.connector_definition
                    action_full_key = f"{connector_def.key}.{action_def.action_key}"
                    run_action_log_messages.append(f"Starting action: {action_def.display_name} (Key: {action_full_key}, Pos: {action_config.position})")

                    resolved_action_config = resolve_template(action_config.config, template_context)
                    run_action_input_data_for_log = resolved_action_config
                    run_action_log_messages.append(f"Resolved config (snippet): {str(resolved_action_config)[:200]}")

                    action_credentials = {}
                    if action_config.connector_id and action_config.connector:
                        raw_creds = action_config.connector.credentials
                        for k, v in raw_creds.items():
                            if k in ['access_token', 'refresh_token', 'client_secret', 'token']: action_credentials[k] = decrypt_value(v)
                            else: action_credentials[k] = v
                        run_action_log_messages.append(f"Using connected service: {action_config.connector.connection_name}")
                    elif connector_def.auth_type and connector_def.auth_type != "none":
                        msg = f"Action '{action_full_key}' requires auth for '{connector_def.display_name}', but no connection configured."
                        run_action_log_messages.append(msg)
                        raise ValueError(msg)

                    action_result = execute_single_action_logic(action_full_key, resolved_action_config, action_credentials)
                    run_action_status = action_result["status"]
                    run_action_output_data = action_result["output_data"]
                    if action_result.get("log_message"): run_action_log_messages.append(action_result["log_message"])
                    
                    context_step_key = f"step_{action_config.position}"
                    template_context["actions"][context_step_key] = {"output": run_action_output_data}

                except Exception as step_exc:
                    run_action_status = "failed"
                    error_message = f"Error in action step (Pos {action_config.position}): {step_exc}"
                    run_action_log_messages.append(error_message)
                    current_app.logger.error(error_message, exc_info=True)
                    if run_action_output_data is None: run_action_output_data = {}
                    run_action_output_data["_error"] = str(step_exc)

                run_action.status = run_action_status
                run_action.finished_at = datetime.utcnow()
                run_action.input_data = run_action_input_data_for_log
                run_action.output_data = run_action_output_data
                run_action.log = "\n".join(run_action_log_messages)

                # If filter is false, workflow should stop executing further actions.
                is_filter_action = action_config.action_definition.connector_definition.key == 'built_in' and action_config.action_definition.action_key == 'filter'
                
                if is_filter_action and run_action_output_data and run_action_output_data.get('filter_passed') is False:
                    overall_run_status = "stopped"
                    current_app.logger.info(f"Filter condition not met for Run ID: {current_run.id}. Stopping workflow execution.")
                    break

                if run_action_status == "failed":
                    overall_run_status = "failed"
                    current_app.logger.warning(f"Action (Pos: {action_config.position}) failed. Run {current_run.id} will be FAILED.")
                    break 
                elif run_action_status == "success" and overall_run_status != "failed" and overall_run_status != "stopped":
                    overall_run_status = "success"

            if overall_run_status == "running" and actions_to_execute: # If loop complete for non-empty actions
                overall_run_status = "success"
            elif not actions_to_execute: # no actions, success by default
                overall_run_status = "success"

            current_run.status = overall_run_status
            current_run.finished_at = datetime.utcnow()
            session.commit()
            current_app.logger.info(f"Workflow Run ID: {current_run.id} finished with status: {current_run.status if current_run.status else 'UNKNOWN'}")

        except Exception as e:
            current_app.logger.error(f"Critical error in execute_workflow_task for workflow_id {workflow_id}: {e}", exc_info=True)
            if current_run:
                current_run.status = "error"
                current_run.finished_at = datetime.utcnow()
            session.rollback()
            try:
                raise self.retry(exc=e)
            except MaxRetriesExceededError:
                current_app.logger.error(f"Max retries for workflow_id {workflow_id} execution. Giving up.")


def execute_single_action_logic(action_definition_key: str, resolved_config: dict, credentials: dict):
    current_app.logger.info(f"Executing action logic for: {action_definition_key} with config: {str(resolved_config)[:200]}")
    action_output = {"status": "failed", "output_data": None, "log_message": ""}

    if action_definition_key == "trello.create_card":
        api_key = credentials.get('api_key')
        token = credentials.get('token')

        idList = resolved_config.get('idList')
        name = resolved_config.get('name')
        pos = resolved_config.get('pos')
        desc = resolved_config.get('desc')
        due = resolved_config.get('due')

        if not idList or not api_key or not token:
            action_output["log_message"] = "Missing Trello API Key. Token or idList"
            return action_output
        
        url = "https://api.trello.com/1/cards"
        headers = {
            "Accept": "application/json"
        }
        query = {'idList': idList, 'key': api_key, 'token': token, 'name': name, 'pos': pos, 'desc': desc, 'due': due}
        
        try:
            trello_response = requests.post(url=url, headers=headers, params=query)
            trello_response.raise_for_status()
            card = trello_response.json()
            current_app.logger.info(f"Trello card created successfully: {card.get('id')}")
            
            action_output["status"] = "success"
            action_output["output_data"] = {
                "card_id": card.get("id"),
                "card_name": card.get("name"),
                "card_url": card.get("shortUrl"),
                "card_desc": card.get("desc"),
                "card_due": card.get("due"),
                "card_labels": [label.get("name") for label in card.get("labels", [])],
                "card_members": [member.get("username") for member in card.get("idMembersVoted", [])]
            }
            action_output["log_message"] = f"Created Trello card: {card.get('name')} (ID: {card.get('id')})"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                action_output["log_message"] = "Unauthorized: Check Trello API Key and Token."
            elif e.response.status_code == 403:
                action_output["log_message"] = "Forbidden: Check Trello permissions or API limits."
            else:
                action_output["log_message"] = f"HTTP error creating Trello card: {e.response.text}"
            current_app.logger.error(action_output["log_message"], exc_info=True)
        except requests.exceptions.RequestException as e:
            action_output["log_message"] = f"Network error creating Trello card: {e}"
            current_app.logger.error(action_output["log_message"], exc_info=True)
        return action_output

    elif action_definition_key == 'built_in.filter':
        conditions = resolved_config.get('conditions', [])
        if not conditions:
            action_output["status"] = "success"
            action_output["log_message"] = "Filter: No conditions provided, passing."
            action_output["output_data"] = {"filter_passed": True, "message": "No conditions."}
            return action_output
        
        all_passed = True
        condition_results_log = []

        for idx, cond in enumerate(conditions):
            input_val_str = str(cond.get('input_value', ''))
            operator = cond.get('operator')
            target_val_str = str(cond.get('target_value', ''))

            passed_this_condition = False

            try:
                num_input = float(input_val_str)
                num_target = float(target_val_str)
            except ValueError:
                num_input, num_target = None, None

            log_entry = f"Cond {idx+1}: Input='{str(input_val_str)[:50]}', Op='{operator}', Target='{str(target_val_str)[:50]}'"

            if operator == "equals":
                passed_this_condition = input_val_str == target_val_str
            elif operator == "not_equals":
                passed_this_condition = input_val_str != target_val_str
            elif operator == "contains":
                passed_this_condition = target_val_str in input_val_str
            elif operator == "not_contains":
                passed_this_condition = target_val_str not in input_val_str
            elif operator == "starts_with":
                passed_this_condition = input_val_str.startswith(target_val_str)
            elif operator == "ends_with":
                passed_this_condition = input_val_str.endswith(target_val_str)
            elif operator == "is_empty":
                passed_this_condition = not input_val_str
            elif operator == "is_not_empty":
                passed_this_condition = bool(input_val_str)
            elif operator == "is_true":
                passed_this_condition = input_val_str.lower() in ['true', '1', 'yes', 'on']
            elif operator == "is_false":
                passed_this_condition = input_val_str.lower() in ['false', '0', 'no', 'off', '']
            elif num_input is not None and num_target is not None: # Numerical comparisons
                if operator == "greater_than":
                    passed_this_condition = num_input > num_target
                elif operator == "less_than":
                    passed_this_condition = num_input < num_target
                elif operator == "greater_than_or_equals":
                    passed_this_condition = num_input >= num_target
                elif operator == "less_than_or_equals":
                    passed_this_condition = num_input <= num_target
                else:
                    log_entry += " (Error: Unknown numeric operator or type mismatch)"
                    all_passed = False # Invalid operator for numbers
            else: # Operator not matched or types were unsuitable for numeric
                if operator in ["greater_than", "less_than", "greater_than_or_equals", "less_than_or_equals"]:
                    log_entry += " (Error: Non-numeric inputs for numeric comparison)"
                else: # Unknown operator overall
                    log_entry += " (Error: Unknown operator)"
                all_passed = False # Invalid operator

            log_entry += f" -> {'Passed' if passed_this_condition else 'Failed'}"
            condition_results_log.append(log_entry)

            if not passed_this_condition:
                all_passed = False

        action_output["log_message"] = "Filter evaluation:\n" + "\n".join(condition_results_log)
        if all_passed:
            action_output["status"] = "success"
            action_output["log_message"] += "\nFilter: All conditions PASSED."
            action_output["output_data"] = {"filter_passed": True, "message": "All conditions met."}
        else:
            # output_data indicates filter failed.
            action_output["status"] = "success" # The filter action itself succeeded in evaluating
            action_output["log_message"] += "\nFilter: At least one condition FAILED. Workflow will stop here."
            action_output["output_data"] = {"filter_passed": False, "message": "One or more conditions not met."}
        return action_output
    
    elif action_definition_key == 'built_in.delay':
        import time
        from dateutil import parser as dateutil_parser

        delay_type = resolved_config.get("delay_type", "for_duration")
        delay_seconds = 0

        if delay_type == 'for_duration':
            duration_seconds = resolved_config.get('duration_seconds')
            if not isinstance(duration_seconds, int) or duration_seconds <= 0:
                action_output["log_message"] = "Delay: Invalid or missing 'duration_seconds'."
                action_output["output_data"] = {"error": "Invalid duration_seconds"}
                return action_output
            delay_seconds = duration_seconds
            action_output["log_message"] = f"Delaying for {delay_seconds} seconds."
        
        elif delay_type == 'until_duration':
            delay_until_iso = resolved_config.get("delay_until_iso")
            if not delay_until_iso:
                action_output["log_message"] = "Delay: Missing 'delay_until_iso'."
                action_output["output_data"] = {"error": "Missing delay_until_iso"}
                return action_output
            try:
                target_time_utc = dateutil_parser.isoparse(delay_until_iso)
                if target_time_utc.tzinfo is None:
                    target_time_utc = target_time_utc.replace(tzinfo=datetime.timezone.utc)
                else:
                    target_time_utc = target_time_utc.astimezone(datetime.timezone.utc)

                now_utc = datetime.now(datetime.timezone.utc)
                if target_time_utc <= now_utc:
                    action_output["log_message"] = f"Delay: Target time '{delay_until_iso}' is in the past or now. No delay."
                    delay_seconds = 0
                else:
                    delay_seconds = (target_time_utc - now_utc).total_seconds()
                    action_output["log_message"] = f"Delaying until {delay_until_iso} (approx. {delay_seconds:.2f} seconds from now)."
            except ValueError as e:
                action_output["log_message"] = f"Delay: Invalid ISO datetime format for 'delay_until_iso': {e}."
                action_output["output_data"] = {"error": f"Invalid delay_until_iso format: {e}"}
                return action_output
        else:
            action_output["log_message"] = f"Delay: Unknown delay_type '{delay_type}'."
            action_output["output_data"] = {"error": f"Unknown delay_type: {delay_type}"}
            return action_output

        if delay_seconds > 0:
            current_app.logger.info(action_output["log_message"])
            # This simple sleep is fine for short delays within a task.
            time.sleep(delay_seconds) 
            # TODO" for long delays, Celery's ETA/countdown is better.

        action_output["status"] = "success"
        action_output["output_data"] = {"delay_completed_at": datetime.utcnow().isoformat() + "Z"}
        action_output["log_message"] += f"\nDelay completed at {action_output['output_data']['delay_completed_at']}."
        current_app.logger.info("Delay action finished.")
        return action_output
    
    else:
        action_output["log_message"] = f"Action logic not implemented for: {action_definition_key}"
        action_output["output_data"] = {"error": "Action not implemented"}
        return action_output