import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/runs')({
  component: WorkflowRuns,
})

function WorkflowRuns() {
  return <div>Hello "/_layout/runs"!</div>
}
