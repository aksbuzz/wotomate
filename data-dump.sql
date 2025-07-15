-- Adminer 5.3.0 PostgreSQL 17.5 dump

DROP TABLE IF EXISTS "action";
DROP SEQUENCE IF EXISTS action_id_seq;
CREATE SEQUENCE action_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 5 CACHE 1;

CREATE TABLE "public"."action" (
    "id" integer DEFAULT nextval('action_id_seq') NOT NULL,
    "workflow_id" integer NOT NULL,
    "action_definition_id" integer NOT NULL,
    "position" integer NOT NULL,
    "config" json NOT NULL,
    "connector_id" integer,
    "created_at" timestamp,
    "updated_at" timestamp,
    CONSTRAINT "action_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX _action_position_uc ON public.action USING btree (workflow_id, "position");

INSERT INTO "action" ("id", "workflow_id", "action_definition_id", "position", "config", "connector_id", "created_at", "updated_at") VALUES
(4,	1,	4,	0,	'{"conditions": [{"input_value": "{{trigger.output.labels | join('','')}}", "operator": "contains", "target_value": "bug"}]}',	3,	'2025-06-15 14:07:59.922603',	'2025-06-15 14:07:59.922603'),
(1,	1,	3,	1,	'{"idList": "68403d506f0ed40da180f986", "name": "{{trigger.output.title}}", "desc": "{{trigger.output.body}} \n\n url: {{trigger.output.url}} \n\n {{actions.step_0.output.message}}", "pos": "top", "due": ""}',	3,	'2025-06-07 13:56:09.16597',	'2025-06-07 13:56:09.16597');

DROP TABLE IF EXISTS "action_definition";
DROP SEQUENCE IF EXISTS action_definition_id_seq;
CREATE SEQUENCE action_definition_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 6 CACHE 1;

CREATE TABLE "public"."action_definition" (
    "id" integer DEFAULT nextval('action_definition_id_seq') NOT NULL,
    "connector_definition_id" integer NOT NULL,
    "action_key" character varying(100) NOT NULL,
    "display_name" character varying(100) NOT NULL,
    "description" text,
    "config_schema" json NOT NULL,
    "input_schema" json,
    "output_schema" json NOT NULL,
    CONSTRAINT "action_definition_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX _connector_action_key_uc ON public.action_definition USING btree (connector_definition_id, action_key);

INSERT INTO "action_definition" ("id", "connector_definition_id", "action_key", "display_name", "description", "config_schema", "input_schema", "output_schema") VALUES
(1,	3,	'send_email',	'Send an Email',	'Sends an email using the connected Gmail account.',	'{"type": "object", "properties": {"to_address": {"type": "string", "format": "email", "title": "To"}, "cc_address": {"type": "string", "format": "email", "title": "CC (Optional)"}, "bcc_address": {"type": "string", "format": "email", "title": "BCC (Optional)"}, "subject": {"type": "string", "title": "Subject"}, "body_html": {"type": "string", "title": "Body (HTML)", "format": "textarea"}, "body_text": {"type": "string", "title": "Body (Plain Text - Optional)", "format": "textarea"}}, "required": ["to_address", "subject"]}',	'{"type": "object", "properties": {"to_address": {"type": "string"}, "cc_address": {"type": "string"}, "bcc_address": {"type": "string"}, "subject": {"type": "string"}, "body_html": {"type": "string"}, "body_text": {"type": "string"}}}',	'{"type": "object", "properties": {"message_id": {"type": "string", "description": "ID of the sent email"}, "status": {"type": "string", "enum": ["sent", "failed"], "description": "Sending status"}}}'),
(2,	4,	'send_channel_message',	'Send Message to Channel',	'Posts a message to a specified Slack channel.',	'{"type": "object", "properties": {"channel_id": {"type": "string", "title": "Channel ID (e.g., C1234567890) or Name (e.g., #general)"}, "message_text": {"type": "string", "title": "Message Text", "format": "textarea"}, "as_user": {"type": "boolean", "title": "Send as authenticated user (bot default)", "default": false}}, "required": ["channel_id", "message_text"]}',	'{"type": "object", "properties": {"channel_id": {"type": "string"}, "message_text": {"type": "string"}, "as_user": {"type": "boolean"}}}',	'{"type": "object", "properties": {"message_ts": {"type": "string", "description": "Timestamp of the sent message"}, "channel_id": {"type": "string", "description": "ID of the channel where message was sent"}, "status": {"type": "string", "enum": ["sent", "failed"]}}}'),
(3,	5,	'create_card',	'Create Trello Card',	'Creates a new card on a specified Trello list.',	'{"type":"object","properties":{"idList":{"type":"string","title":"List ID","description":"The ID of the list to add the card to."},"name":{"type":"string","title":"Card Name"},"desc":{"type":"string","title":"Card Description (Optional)","format":"textarea"},"pos":{"type":"string","enum":["top","bottom"],"title":"Position (Optional)","default":"bottom"},"due":{"type":"string","format":"date-time","title":"Due Date (Optional)"}},"required":["idList","name"]}',	'{"type":"object","properties":{"idList":{"type":"string"},"name":{"type":"string"},"desc":{"type":"string"},"pos":{"type":"string"},"due":{"type":"string"}}}',	'{"type":"object","properties":{"id":{"type":"string","description":"ID of the created card"},"name":{"type":"string","description":"Name of the created card"},"shortUrl":{"type":"string","description":"Short URL of the card"},"idList":{"type":"string"}}}'),
(4,	6,	'filter',	'Filter (If conditions match)',	'Continues the workflow only if specified conditions are met. Otherwise, stops.',	'{"type":"object","properties":{"conditions":{"type":"array","title":"Conditions (All must be true - AND logic)","items":{"type":"object","properties":{"input_value":{"type":"string","title":"Input Value (e.g., {{ trigger.output.status }})"},"operator":{"type":"string","title":"Operator","enum":["equals","not_equals","contains","not_contains","starts_with","ends_with","is_empty","is_not_empty","greater_than","less_than","greater_than_or_equals","less_than_or_equals","is_true","is_false"]},"target_value":{"type":"string","title":"Target Value (leave empty for unary operators like is_empty, is_true)"}},"required":["input_value","operator"]}}},"required":["conditions"]}',	'{"type":"object","properties":{"any_value":{"type":["string","number","boolean","null"],"description":"Any value from trigger or previous steps."}}}',	'{"type":"object","properties":{"filter_passed":{"type":"boolean","description":"True if all conditions passed, False otherwise."},"message":{"type":"string","description":"Reason for filter result."}}}'),
(5,	6,	'delay',	'Delay',	'Pauses the workflow for a specified duration or until a specific time.',	'{"type":"object","properties":{"delay_type":{"type":"string","title":"Delay Type","enum":["for_duration","until_datetime"],"default":"for_duration"},"duration_seconds":{"type":"integer","title":"Delay For (seconds)","description":"Used if type == for_duration"},"delay_until_iso":{"type":"string","title":"Delay Until (ISO 8601 Datetime)","format":"date-time","description":"e.g., 2024-03-15T10:00:00Z. Used if type == until_datetime"}},"required":["delay_type"]}',	'{}',	'{"type":"object","properties":{"delay_completed_at":{"type":"string","format":"date-time","description":"Timestamp when delay finished."}}}');

DROP TABLE IF EXISTS "alembic_version";
CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL,
    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
)
WITH (oids = false);

INSERT INTO "alembic_version" ("version_num") VALUES
('e98f067cead5');

DROP TABLE IF EXISTS "connector";
DROP SEQUENCE IF EXISTS connector_id_seq;
CREATE SEQUENCE connector_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 4 CACHE 1;

CREATE TABLE "public"."connector" (
    "id" integer DEFAULT nextval('connector_id_seq') NOT NULL,
    "user_id" integer NOT NULL,
    "connector_key" character varying(50) NOT NULL,
    "connection_name" character varying(100),
    "credentials" json NOT NULL,
    "created_at" timestamp,
    "updated_at" timestamp,
    CONSTRAINT "connector_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX _user_connector_key_uc ON public.connector USING btree (user_id, connector_key);

INSERT INTO "connector" ("id", "user_id", "connector_key", "connection_name", "credentials", "created_at", "updated_at") VALUES
(1,	1,	'github',	'GitHub (aksbuzz)',	'{"access_token": "gAAAAABoPxeYDM1drJRstgy3Unrssx8apWUXtQ8hAMoApCLH0sjCWIBTsUmWXQq-lrkqcQYIEl096ofRqmzi0lRYKeSZrCVunVoAbjtxQ-g_9sxFDPeadGlD0ASqOrXS-ircyP7rbiYJ", "scopes": ["read:user", "repo", "user:email"], "token_type": "bearer", "github_user_id": 20378257, "github_login": "aksbuzz"}',	'2025-06-03 15:41:12.812508',	'2025-06-03 15:41:12.812508'),
(3,	1,	'trello',	'Trello (akshay07549871)',	'{"api_key": "aa088c9ccd2821d83daf3d79866dcb08", "token": "gAAAAABoQRu7J82GZoyXTH_64b5u_IuTOHagMSjiO9vHgPaOBBZgfmlGx1qC3PjhYTYYbyHTYtIF3NQ7rVBh_wloX1WWDrXLfltK0spY9lb81kQEigk4Me2duDkgFMoNSxXMRpQskYrSIzS2-Il3xNfUfBNUx2M4RBDgnSlQm3RB3J_rckI7hmg=", "trello_member_id": "684024a41a9bc8397b058f48", "trello_username": "akshay07549871"}',	'2025-06-05 04:23:23.246523',	'2025-06-05 04:23:23.246523');

DROP TABLE IF EXISTS "connector_definition";
DROP SEQUENCE IF EXISTS connector_definition_id_seq;
CREATE SEQUENCE connector_definition_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 7 CACHE 1;

CREATE TABLE "public"."connector_definition" (
    "id" integer DEFAULT nextval('connector_definition_id_seq') NOT NULL,
    "key" character varying(50) NOT NULL,
    "display_name" character varying(100) NOT NULL,
    "description" text,
    "auth_type" character varying(50),
    "connector_config_schema" json,
    "logo_url" character varying(255),
    CONSTRAINT "connector_definition_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ix_connector_definition_key ON public.connector_definition USING btree (key);

INSERT INTO "connector_definition" ("id", "key", "display_name", "description", "auth_type", "connector_config_schema", "logo_url") VALUES
(1,	'github',	'GitHub',	'Connect your GitHub account to trigger workflows on repository events or perform actions.',	'oauth2',	NULL,	'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'),
(2,	'inbound_webhook',	'Inbound Webhook',	'Trigger workflows when a unique URL receives an HTTP POST request.',	'none',	NULL,	'https://your_domain.com/static/images/webhook_icon.png'),
(3,	'gmail',	'Gmail',	'Connect your Gmail account to send emails or manage your inbox.',	'oauth2',	NULL,	'https://your_domain.com/static/images/gmail_icon.png'),
(4,	'slack',	'Slack',	'Connect your Slack workspace to send messages.',	'oauth2',	NULL,	'https://your_domain.com/static/images/slack_icon.png'),
(5,	'trello',	'Trello',	'Connect your Trello account to manage boards, lists, and cards.',	'api-key',	NULL,	NULL),
(6,	'built_in',	'Built-in',	'Built-in workflow control and utility actions.',	'none',	NULL,	NULL);

DROP TABLE IF EXISTS "trigger";
DROP SEQUENCE IF EXISTS trigger_id_seq;
CREATE SEQUENCE trigger_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 2 CACHE 1;

CREATE TABLE "public"."trigger" (
    "id" integer DEFAULT nextval('trigger_id_seq') NOT NULL,
    "workflow_id" integer NOT NULL,
    "trigger_definition_id" integer NOT NULL,
    "config" json,
    "connector_id" integer,
    "webhook_id" character varying(36),
    "created_at" timestamp,
    "updated_at" timestamp,
    "last_polled_at" timestamp,
    "polling_state" json,
    CONSTRAINT "trigger_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ix_trigger_webhook_id ON public.trigger USING btree (webhook_id);

INSERT INTO "trigger" ("id", "workflow_id", "trigger_definition_id", "config", "connector_id", "webhook_id", "created_at", "updated_at", "last_polled_at", "polling_state") VALUES
(1,	1,	1,	'{"repository_name": "interview_prep", "repository_owner": "aksbuzz"}',	1,	NULL,	'2025-06-04 06:32:30.219733',	'2025-06-16 17:57:01.629319',	'2025-06-16 17:57:01.613315',	'{"last_seen_issue_created_at": "2025-06-15T14:39:45Z"}');

DROP TABLE IF EXISTS "trigger_definition";
DROP SEQUENCE IF EXISTS trigger_definition_id_seq;
CREATE SEQUENCE trigger_definition_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 4 CACHE 1;

CREATE TABLE "public"."trigger_definition" (
    "id" integer DEFAULT nextval('trigger_definition_id_seq') NOT NULL,
    "connector_definition_id" integer NOT NULL,
    "event_key" character varying(100) NOT NULL,
    "display_name" character varying(100) NOT NULL,
    "description" text,
    "config_schema" json NOT NULL,
    "output_schema" json NOT NULL,
    "requires_webhook_endpoint" boolean NOT NULL,
    CONSTRAINT "trigger_definition_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX _connector_event_key_uc ON public.trigger_definition USING btree (connector_definition_id, event_key);

INSERT INTO "trigger_definition" ("id", "connector_definition_id", "event_key", "display_name", "description", "config_schema", "output_schema", "requires_webhook_endpoint") VALUES
(1,	1,	'new_issue',	'New Issue',	'Triggers when a new issue is created in a selected repository.',	'{"type": "object", "properties": {"repository_owner": {"type": "string", "title": "Repository Owner"}, "repository_name": {"type": "string", "title": "Repository Name"}}, "required": ["repository_owner", "repository_name"]}',	'{"type": "object", "properties": {"issue_id": {"type": "integer", "description": "ID of the issue"}, "issue_number": {"type": "integer", "description": "Number of the issue"}, "title": {"type": "string", "description": "Title of the issue"}, "body": {"type": "string", "description": "Body content of the issue"}, "url": {"type": "string", "format": "uri", "description": "URL of the issue"}, "user_login": {"type": "string", "description": "Login of the user who created the issue"}, "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels on the issue"}}}',	'0'),
(2,	1,	'new_pull_request',	'New Pull Request Opened',	'Triggers when a new pull request is opened or synchronized in a selected repository.',	'{"type": "object", "properties": {"repository_owner": {"type": "string", "title": "Repository Owner"}, "repository_name": {"type": "string", "title": "Repository Name"}}, "required": ["repository_owner", "repository_name"]}',	'{"type": "object", "properties": {"pr_id": {"type": "integer", "description": "ID of the pull request"}, "pr_number": {"type": "integer", "description": "Number of the pull request"}, "title": {"type": "string", "description": "Title of the pull request"}, "body": {"type": "string", "description": "Body content of the pull request"}, "url": {"type": "string", "format": "uri", "description": "URL of the pull request"}, "user_login": {"type": "string", "description": "Login of the user who opened the PR"}, "state": {"type": "string", "description": "State (e.g., open, closed)"}, "source_branch": {"type": "string"}, "target_branch": {"type": "string"}}}',	'0'),
(3,	2,	'http_request_received',	'Webhook Called',	'Triggers when the workflow''s unique webhook URL is called.',	'{"type": "object", "properties": {"expected_payload_schema": {"type": "object", "title": "Expected Payload JSON Schema (Optional)", "description": "Define a JSON schema to validate incoming webhook payloads and provide typed outputs."}}}',	'{"type": "object", "properties": {"body": {"type": ["object", "array", "string", "number", "boolean", "null"], "description": "Parsed JSON body or raw body if not JSON"}, "headers": {"type": "object", "description": "Request headers"}, "query_params": {"type": "object", "description": "URL query parameters"}, "method": {"type": "string", "description": "HTTP method (e.g., POST, GET)"}}}',	'1');

DROP TABLE IF EXISTS "user";
DROP SEQUENCE IF EXISTS user_id_seq;
CREATE SEQUENCE user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 2 CACHE 1;

CREATE TABLE "public"."user" (
    "id" integer DEFAULT nextval('user_id_seq') NOT NULL,
    "email" character varying(120) NOT NULL,
    "password_hash" character varying(128) NOT NULL,
    "created_at" timestamp,
    CONSTRAINT "user_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX user_email_key ON public."user" USING btree (email);

INSERT INTO "user" ("id", "email", "password_hash", "created_at") VALUES
(1,	'first@gmail.com',	'$2b$12$7BXt/9N8V8RsxmE1wGb1qeUcs9mhiL64kc5Fe/My/hlZlhD2dzdfm',	'2025-06-01 09:05:44.741377');

DROP TABLE IF EXISTS "workflow";
DROP SEQUENCE IF EXISTS workflow_id_seq;
CREATE SEQUENCE workflow_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 2 CACHE 1;

CREATE TABLE "public"."workflow" (
    "id" integer DEFAULT nextval('workflow_id_seq') NOT NULL,
    "name" character varying(120) NOT NULL,
    "user_id" integer NOT NULL,
    "is_active" boolean NOT NULL,
    "created_at" timestamp,
    "updated_at" timestamp,
    "status" character varying(100) NOT NULL,
    CONSTRAINT "workflow_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

INSERT INTO "workflow" ("id", "name", "user_id", "is_active", "created_at", "updated_at", "status") VALUES
(1,	'Create Trello card on New GitHub Issue',	1,	'1',	'2025-06-04 06:02:39.684045',	'2025-06-05 05:49:32.246433',	'draft');

DROP TABLE IF EXISTS "workflow_run";
DROP SEQUENCE IF EXISTS workflow_run_id_seq;
CREATE SEQUENCE workflow_run_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 11 CACHE 1;

CREATE TABLE "public"."workflow_run" (
    "id" integer DEFAULT nextval('workflow_run_id_seq') NOT NULL,
    "workflow_id" integer NOT NULL,
    "status" character varying(100) NOT NULL,
    "trigger_event_data" json,
    "started_at" timestamp,
    "finished_at" timestamp,
    CONSTRAINT "workflow_run_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

INSERT INTO "workflow_run" ("id", "workflow_id", "status", "trigger_event_data", "started_at", "finished_at") VALUES
(1,	1,	'success',	'{"issue_id": 3128084996, "issue_number": 1, "title": "First Test Issue", "body": "Lorem Ipsum dolor st imet", "url": "https://github.com/aksbuzz/interview_prep/issues/1", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-12 19:25:50.745632',	'2025-06-12 19:25:52.175163'),
(2,	1,	'success',	'{"issue_id": 3128085611, "issue_number": 2, "title": "Test Issue 2", "body": "Lorem ipsum dolor st imet", "url": "https://github.com/aksbuzz/interview_prep/issues/2", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-12 19:25:52.32561',	'2025-06-12 19:25:53.519054'),
(3,	1,	'success',	'{"issue_id": 3128084996, "issue_number": 1, "title": "First Test Issue", "body": "Lorem Ipsum dolor st imet", "url": "https://github.com/aksbuzz/interview_prep/issues/1", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-12 19:34:52.986694',	'2025-06-12 19:34:54.510274'),
(4,	1,	'success',	'{"issue_id": 3128085611, "issue_number": 2, "title": "Test Issue 2", "body": "Lorem ipsum dolor st imet", "url": "https://github.com/aksbuzz/interview_prep/issues/2", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-12 19:34:54.642252',	'2025-06-12 19:34:55.8787'),
(5,	1,	'success',	'{"issue_id": 3143804489, "issue_number": 3, "title": "Third Issue", "body": "This is a third issue description", "url": "https://github.com/aksbuzz/interview_prep/issues/3", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-13 14:45:01.378901',	'2025-06-13 14:45:02.958406'),
(6,	1,	'success',	'{"issue_id": 3147605562, "issue_number": 4, "title": "This is a test issue.", "body": "Lorem ipsum dolor st imett.", "url": "https://github.com/aksbuzz/interview_prep/issues/4", "user_login": "aksbuzz", "labels": ["bug"], "repository_name": "interview_prep"}',	'2025-06-15 14:22:01.423626',	'2025-06-15 14:22:02.844962'),
(7,	1,	'success',	'{"issue_id": 3147606744, "issue_number": 5, "title": "This is another test issue", "body": "Not a bug", "url": "https://github.com/aksbuzz/interview_prep/issues/5", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-15 14:22:03.010271',	'2025-06-15 14:22:04.215178'),
(8,	1,	'failed',	'{"issue_id": 3147618811, "issue_number": 6, "title": "This is bug issue", "body": "Lorem", "url": "https://github.com/aksbuzz/interview_prep/issues/6", "user_login": "aksbuzz", "labels": ["bug"], "repository_name": "interview_prep"}',	'2025-06-15 14:37:01.488037',	'2025-06-15 14:37:01.695674'),
(9,	1,	'stopped',	'{"issue_id": 3147618969, "issue_number": 7, "title": "This is a normal issue", "body": "Lorem", "url": "https://github.com/aksbuzz/interview_prep/issues/7", "user_login": "aksbuzz", "labels": [], "repository_name": "interview_prep"}',	'2025-06-15 14:37:01.829311',	'2025-06-15 14:37:01.868942'),
(10,	1,	'success',	'{"issue_id": 3147629883, "issue_number": 8, "title": "Bug Issue", "body": null, "url": "https://github.com/aksbuzz/interview_prep/issues/8", "user_login": "aksbuzz", "labels": ["bug"], "repository_name": "interview_prep"}',	'2025-06-15 14:43:01.574986',	'2025-06-15 14:43:02.953231');

DROP TABLE IF EXISTS "workflow_run_action";
DROP SEQUENCE IF EXISTS workflow_run_action_id_seq;
CREATE SEQUENCE workflow_run_action_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 15 CACHE 1;

CREATE TABLE "public"."workflow_run_action" (
    "id" integer DEFAULT nextval('workflow_run_action_id_seq') NOT NULL,
    "run_id" integer NOT NULL,
    "action_id" integer NOT NULL,
    "position" integer NOT NULL,
    "status" character varying(100) NOT NULL,
    "started_at" timestamp,
    "finished_at" timestamp,
    "input_data" json,
    "output_data" json,
    "log" text,
    CONSTRAINT "workflow_run_action_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

INSERT INTO "workflow_run_action" ("id", "run_id", "action_id", "position", "status", "started_at", "finished_at", "input_data", "output_data", "log") VALUES
(1,	1,	1,	0,	'success',	'2025-06-12 19:25:50.765011',	'2025-06-12 19:25:52.175163',	'{"idList": "68403d506f0ed40da180f986", "name": "First Test Issue", "desc": "Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1", "pos": "top", "due": "2025-06-10T13:54:00.000Z"}',	'{"card_id": "684b29bed872ca8859b820f4", "card_name": "First Test Issue", "card_url": "https://trello.com/c/cQA0SBeV", "card_desc": "Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1", "card_due": "2025-06-10T13:54:00.000Z", "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 0)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''First Test Issue'', ''desc'': ''Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1'', ''pos'': ''top'', ''due'': ''2025-06-10T13
Using connected service: Trello (akshay07549871)
Created Trello card: First Test Issue (ID: 684b29bed872ca8859b820f4)'),
(2,	2,	1,	0,	'success',	'2025-06-12 19:25:52.347106',	'2025-06-12 19:25:53.519054',	'{"idList": "68403d506f0ed40da180f986", "name": "Test Issue 2", "desc": "Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2", "pos": "top", "due": "2025-06-10T13:54:00.000Z"}',	'{"card_id": "684b29bfac97d8ab22538b8e", "card_name": "Test Issue 2", "card_url": "https://trello.com/c/unWVLJho", "card_desc": "Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2", "card_due": "2025-06-10T13:54:00.000Z", "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 0)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''Test Issue 2'', ''desc'': ''Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2'', ''pos'': ''top'', ''due'': ''2025-06-10T13:54:
Using connected service: Trello (akshay07549871)
Created Trello card: Test Issue 2 (ID: 684b29bfac97d8ab22538b8e)'),
(3,	3,	1,	0,	'success',	'2025-06-12 19:34:53.000103',	'2025-06-12 19:34:54.510274',	'{"idList": "68403d506f0ed40da180f986", "name": "First Test Issue", "desc": "Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1", "pos": "top", "due": "2025-06-10T13:54:00.000Z"}',	'{"card_id": "684b2bdd4fd4aee983e2971c", "card_name": "First Test Issue", "card_url": "https://trello.com/c/jtO9DCpG", "card_desc": "Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1", "card_due": "2025-06-10T13:54:00.000Z", "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 0)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''First Test Issue'', ''desc'': ''Lorem Ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/1'', ''pos'': ''top'', ''due'': ''2025-06-10T13
Using connected service: Trello (akshay07549871)
Created Trello card: First Test Issue (ID: 684b2bdd4fd4aee983e2971c)'),
(4,	4,	1,	0,	'success',	'2025-06-12 19:34:54.653072',	'2025-06-12 19:34:55.8787',	'{"idList": "68403d506f0ed40da180f986", "name": "Test Issue 2", "desc": "Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2", "pos": "top", "due": "2025-06-10T13:54:00.000Z"}',	'{"card_id": "684b2bdebc438e8f2e141240", "card_name": "Test Issue 2", "card_url": "https://trello.com/c/exftYBsi", "card_desc": "Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2", "card_due": "2025-06-10T13:54:00.000Z", "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 0)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''Test Issue 2'', ''desc'': ''Lorem ipsum dolor st imet \n\n url: https://github.com/aksbuzz/interview_prep/issues/2'', ''pos'': ''top'', ''due'': ''2025-06-10T13:54:
Using connected service: Trello (akshay07549871)
Created Trello card: Test Issue 2 (ID: 684b2bdebc438e8f2e141240)'),
(5,	5,	1,	0,	'success',	'2025-06-13 14:45:01.396046',	'2025-06-13 14:45:02.958406',	'{"idList": "68403d506f0ed40da180f986", "name": "Third Issue", "desc": "This is a third issue description \n\n url: https://github.com/aksbuzz/interview_prep/issues/3", "pos": "top", "due": "2025-06-10T13:54:00.000Z"}',	'{"card_id": "684c396e868db99e64471204", "card_name": "Third Issue", "card_url": "https://trello.com/c/qNddbWDr", "card_desc": "This is a third issue description \n\n url: https://github.com/aksbuzz/interview_prep/issues/3", "card_due": "2025-06-10T13:54:00.000Z", "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 0)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''Third Issue'', ''desc'': ''This is a third issue description \n\n url: https://github.com/aksbuzz/interview_prep/issues/3'', ''pos'': ''top'', ''due'': ''2025-06-10
Using connected service: Trello (akshay07549871)
Created Trello card: Third Issue (ID: 684c396e868db99e64471204)'),
(6,	6,	4,	0,	'success',	'2025-06-15 14:22:01.44061',	'2025-06-15 14:22:01.505976',	'{"input_value": "bug", "operator": "contains", "target_value": "bug"}',	'{"filter_passed": true, "message": "No conditions."}',	'Starting action: Filter (If conditions match) (Key: built_in.filter, Pos: 0)
Resolved config (snippet): {''input_value'': ''bug'', ''operator'': ''contains'', ''target_value'': ''bug''}
Using connected service: Trello (akshay07549871)
Filter: No conditions provided, passing.'),
(7,	6,	1,	1,	'success',	'2025-06-15 14:22:01.505976',	'2025-06-15 14:22:02.831283',	'{"idList": "68403d506f0ed40da180f986", "name": "This is a test issue.", "desc": "Lorem ipsum dolor st imett. \n\n url: https://github.com/aksbuzz/interview_prep/issues/4", "pos": "top", "due": ""}',	'{"card_id": "684ed708beb834e89f5e8f50", "card_name": "This is a test issue.", "card_url": "https://trello.com/c/EZhcj9NO", "card_desc": "Lorem ipsum dolor st imett. \n\n url: https://github.com/aksbuzz/interview_prep/issues/4", "card_due": null, "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 1)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''This is a test issue.'', ''desc'': ''Lorem ipsum dolor st imett. \n\n url: https://github.com/aksbuzz/interview_prep/issues/4'', ''pos'': ''top'', ''due'': ''''}
Using connected service: Trello (akshay07549871)
Created Trello card: This is a test issue. (ID: 684ed708beb834e89f5e8f50)'),
(8,	7,	4,	0,	'success',	'2025-06-15 14:22:03.025735',	'2025-06-15 14:22:03.046268',	'{"input_value": "", "operator": "contains", "target_value": "bug"}',	'{"filter_passed": true, "message": "No conditions."}',	'Starting action: Filter (If conditions match) (Key: built_in.filter, Pos: 0)
Resolved config (snippet): {''input_value'': '''', ''operator'': ''contains'', ''target_value'': ''bug''}
Using connected service: Trello (akshay07549871)
Filter: No conditions provided, passing.'),
(9,	7,	1,	1,	'success',	'2025-06-15 14:22:03.046268',	'2025-06-15 14:22:04.215178',	'{"idList": "68403d506f0ed40da180f986", "name": "This is another test issue", "desc": "Not a bug \n\n url: https://github.com/aksbuzz/interview_prep/issues/5", "pos": "top", "due": ""}',	'{"card_id": "684ed709cee683de9006983e", "card_name": "This is another test issue", "card_url": "https://trello.com/c/f2KS5YS1", "card_desc": "Not a bug \n\n url: https://github.com/aksbuzz/interview_prep/issues/5", "card_due": null, "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 1)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''This is another test issue'', ''desc'': ''Not a bug \n\n url: https://github.com/aksbuzz/interview_prep/issues/5'', ''pos'': ''top'', ''due'': ''''}
Using connected service: Trello (akshay07549871)
Created Trello card: This is another test issue (ID: 684ed709cee683de9006983e)'),
(10,	8,	4,	0,	'success',	'2025-06-15 14:37:01.507953',	'2025-06-15 14:37:01.537145',	'{"conditions": [{"input_value": "bug", "operator": "contains", "target_value": "bug"}]}',	'{"filter_passed": true, "message": "All conditions met."}',	'Starting action: Filter (If conditions match) (Key: built_in.filter, Pos: 0)
Resolved config (snippet): {''conditions'': [{''input_value'': ''bug'', ''operator'': ''contains'', ''target_value'': ''bug''}]}
Using connected service: Trello (akshay07549871)
Filter evaluation:
Cond 1: Input=''bug'', Op=''contains'', Target=''bug'' -> Passed
Filter: All conditions PASSED.'),
(11,	8,	1,	1,	'failed',	'2025-06-15 14:37:01.537145',	'2025-06-15 14:37:01.695674',	'{}',	'{"_error": "Error rendering template ''{{trigger.output.body}} \n\n url: {{trigger.output.url}} \n\n {{step_0.output.message}}'': Templating error: ''step_0'' is undefined for template ''{{trigger.output.body}} \n\n url: {{trigger.output.url}} \n\n {{step_0.output.message}}'' with context keys: [''trigger'', ''actions'']"}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 1)
Error in action step (Pos 1): Error rendering template ''{{trigger.output.body}} 

 url: {{trigger.output.url}} 

 {{step_0.output.message}}'': Templating error: ''step_0'' is undefined for template ''{{trigger.output.body}} 

 url: {{trigger.output.url}} 

 {{step_0.output.message}}'' with context keys: [''trigger'', ''actions'']'),
(12,	9,	4,	0,	'success',	'2025-06-15 14:37:01.846888',	'2025-06-15 14:37:01.868942',	'{"conditions": [{"input_value": "", "operator": "contains", "target_value": "bug"}]}',	'{"filter_passed": false, "message": "One or more conditions not met."}',	'Starting action: Filter (If conditions match) (Key: built_in.filter, Pos: 0)
Resolved config (snippet): {''conditions'': [{''input_value'': '''', ''operator'': ''contains'', ''target_value'': ''bug''}]}
Using connected service: Trello (akshay07549871)
Filter evaluation:
Cond 1: Input='''', Op=''contains'', Target=''bug'' -> Failed
Filter: At least one condition FAILED. Workflow will stop here.'),
(13,	10,	4,	0,	'success',	'2025-06-15 14:43:01.586937',	'2025-06-15 14:43:01.60068',	'{"conditions": [{"input_value": "bug", "operator": "contains", "target_value": "bug"}]}',	'{"filter_passed": true, "message": "All conditions met."}',	'Starting action: Filter (If conditions match) (Key: built_in.filter, Pos: 0)
Resolved config (snippet): {''conditions'': [{''input_value'': ''bug'', ''operator'': ''contains'', ''target_value'': ''bug''}]}
Using connected service: Trello (akshay07549871)
Filter evaluation:
Cond 1: Input=''bug'', Op=''contains'', Target=''bug'' -> Passed
Filter: All conditions PASSED.'),
(14,	10,	1,	1,	'success',	'2025-06-15 14:43:01.60068',	'2025-06-15 14:43:02.953231',	'{"idList": "68403d506f0ed40da180f986", "name": "Bug Issue", "desc": "None \n\n url: https://github.com/aksbuzz/interview_prep/issues/8 \n\n All conditions met.", "pos": "top", "due": ""}',	'{"card_id": "684edbf411b56029bdaa09a3", "card_name": "Bug Issue", "card_url": "https://trello.com/c/3JNGDmd6", "card_desc": "None \n\n url: https://github.com/aksbuzz/interview_prep/issues/8 \n\n All conditions met.", "card_due": null, "card_labels": [], "card_members": []}',	'Starting action: Create Trello Card (Key: trello.create_card, Pos: 1)
Resolved config (snippet): {''idList'': ''68403d506f0ed40da180f986'', ''name'': ''Bug Issue'', ''desc'': ''None \n\n url: https://github.com/aksbuzz/interview_prep/issues/8 \n\n All conditions met.'', ''pos'': ''top'', ''due'': ''''}
Using connected service: Trello (akshay07549871)
Created Trello card: Bug Issue (ID: 684edbf411b56029bdaa09a3)');

ALTER TABLE ONLY "public"."action" ADD CONSTRAINT "action_action_definition_id_fkey" FOREIGN KEY (action_definition_id) REFERENCES action_definition(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."action" ADD CONSTRAINT "action_connector_id_fkey" FOREIGN KEY (connector_id) REFERENCES connector(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."action" ADD CONSTRAINT "action_workflow_id_fkey" FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."action_definition" ADD CONSTRAINT "action_definition_connector_definition_id_fkey" FOREIGN KEY (connector_definition_id) REFERENCES connector_definition(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."connector" ADD CONSTRAINT "connector_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."trigger" ADD CONSTRAINT "trigger_connector_id_fkey" FOREIGN KEY (connector_id) REFERENCES connector(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."trigger" ADD CONSTRAINT "trigger_trigger_definition_id_fkey" FOREIGN KEY (trigger_definition_id) REFERENCES trigger_definition(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."trigger" ADD CONSTRAINT "trigger_workflow_id_fkey" FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."trigger_definition" ADD CONSTRAINT "trigger_definition_connector_definition_id_fkey" FOREIGN KEY (connector_definition_id) REFERENCES connector_definition(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."workflow" ADD CONSTRAINT "workflow_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."workflow_run" ADD CONSTRAINT "workflow_run_workflow_id_fkey" FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."workflow_run_action" ADD CONSTRAINT "workflow_run_action_action_id_fkey" FOREIGN KEY (action_id) REFERENCES action(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."workflow_run_action" ADD CONSTRAINT "workflow_run_action_run_id_fkey" FOREIGN KEY (run_id) REFERENCES workflow_run(id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2025-07-15 17:56:50 UTC
