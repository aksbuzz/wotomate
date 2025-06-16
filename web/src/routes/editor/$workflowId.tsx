import { EditorHeader } from '@/components/Editor/header';
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/editor/$workflowId')({
  component: WorkflowEditor,
});

const defaultState = {
  name: "",
  user_id: 0,
  owner: "",
  status: 'draft',
  trigger: {},
  actions: [],
  runs: []
}

function WorkflowEditor() {
  const { workflowId } = Route.useParams();
  const [name, setName] = useState(`Testing ${workflowId}`);

  return (
    <>
      <EditorHeader name={name} onNameChange={e => setName(e.target.value)} />
        {
          !defaultState.trigger && 
        }
    </>
  );
}
