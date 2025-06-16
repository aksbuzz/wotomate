import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/flows')({
  component: Workflows,
})

function Workflows() {
  return <div>Hello "/_layout/workflows"!</div>
}
