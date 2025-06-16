-- 1. Connections
INSERT INTO connections (id,name,type,credentials) VALUES
  ('conn_stripe','Stripe Prod','stripe','{"apiKey":"sk_live_…"}'),
  ('conn_mail','Mailgun','mailgun','{"apiKey":"key-…","domain":"mg.example.com"}'),
  ('conn_aws','AWS CloudWatch','aws','{"accessKeyId":"AKIA…","secretAccessKey":"…"}');

-- 2. Workflow
INSERT INTO workflows (id,name,trigger_id)
VALUES
  ('wf_payments','On Stripe Payment','trig_stripePayment');

-- 3. Trigger config
INSERT INTO trigger_configs (id,workflow_id,type,connection_id,settings)
VALUES
  ('trig_stripePayment','wf_payments','stripe_payment','conn_stripe',
   '{"events":["invoice.payment_succeeded"]}');

-- 4. Actions
INSERT INTO action_configs (id,workflow_id,"order",type,connection_id,settings,input_mappings)
VALUES
  ('act_sendEmail','wf_payments',1,'send_email','conn_mail',
   '{"from":"billing@example.com","subject":"Payment received!"}',
   '{"to":"{{trigger.customer_email}}","body":"Hello {{trigger.customer_name}}, we received your payment of ${{trigger.amount/100}}."}'
  ),
  ('act_logCloudwatch','wf_payments',2,'log_to_cloudwatch','conn_aws',
   '{"logGroupName":"payment-events","logStreamName":"stripe-payments"}',
   '{"message":"Customer {{trigger.customer_id}} paid ${{trigger.amount/100}}; email sent to {{act_sendEmail.status}}"}'
  );

-- 5. Run & Outputs
INSERT INTO runs (id,workflow_id,status,started_at,finished_at)
VALUES
  ('run_001','wf_payments','succeeded','2025-05-28T07:42:00Z','2025-05-28T07:42:05Z');

INSERT INTO step_outputs (run_id,step_type,step_config_id,output)
VALUES
  ('run_001','trigger','trig_stripePayment',
   '{"customer_id":"cus_123","customer_email":"alice@example.com","customer_name":"Alice","amount":4999}'
  ),
  ('run_001','action','act_sendEmail',
   '{"messageId":"mg.abc123","status":"sent"}'
  ),
  ('run_001','action','act_logCloudwatch',
   '{"logEventId":"evt-789","status":"ok"}'
  );