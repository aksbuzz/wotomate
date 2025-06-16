-- 1. Connections to external services
CREATE TABLE connections (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  type          TEXT NOT NULL,           -- e.g. 'stripe', 'mailgun', 'aws'
  credentials   JSONB NOT NULL,          -- encrypted in the app layer
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Workflows
CREATE TABLE workflows (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  trigger_id    UUID NOT NULL REFERENCES trigger_configs(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Trigger configurations
CREATE TABLE trigger_configs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id   UUID UNIQUE NOT NULL REFERENCES workflows(id),
  type          TEXT NOT NULL,           -- e.g. 'stripe_payment'
  connection_id UUID NOT NULL REFERENCES connections(id),
  settings      JSONB NOT NULL,          -- type-specific settings
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Action configurations
CREATE TABLE action_configs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id   UUID NOT NULL REFERENCES workflows(id),
  "order"       INT NOT NULL,            -- position in sequence
  type          TEXT NOT NULL,           -- e.g. 'send_email'
  connection_id UUID NOT NULL REFERENCES connections(id),
  settings      JSONB NOT NULL,          -- type-specific settings
  input_mappings JSONB NOT NULL,         -- e.g. { "to": "{{trigger.email}}" }
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(workflow_id, "order")
);

-- 5. Execution runs
CREATE TABLE runs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id   UUID NOT NULL REFERENCES workflows(id),
  status        TEXT NOT NULL CHECK (status IN ('running','succeeded','failed')),
  started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at   TIMESTAMPTZ
);

-- 6. Step outputs
CREATE TABLE step_outputs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id        UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
  step_type     TEXT NOT NULL CHECK (step_type IN ('trigger','action')),
  step_config_id UUID NOT NULL,          -- FK to trigger_configs or action_configs
  output        JSONB NOT NULL,          -- arbitrary key/value outputs
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
