import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/')({
  component: Dashboard,
})

function Dashboard() {
  return <div>Hello "/_layout/"!</div>
}
