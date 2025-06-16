import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/connectors')({
  component: Connectors,
})

function Connectors() {
  return <div>Hello "/_layout/connectors"!</div>
}
