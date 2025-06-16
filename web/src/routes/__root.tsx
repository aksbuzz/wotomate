import { Outlet, createRootRoute } from '@tanstack/react-router'
import { lazy, Suspense } from 'react';

const loadDevtools = () => 
  Promise.all([
    import('@tanstack/react-router-devtools'),
    import('@tanstack/react-query-devtools')
  ]).then(([routerDevtools, reactQueryDevtools]) => {
    return {
      default: () => (
        <>
          <routerDevtools.TanStackRouterDevtools />
          <reactQueryDevtools.ReactQueryDevtools />
        </>
      )
    }
  })

const TanStackDevtools = import.meta.env.PROD ? () => null : lazy(loadDevtools)

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <Suspense>
        <TanStackDevtools />
      </Suspense>
    </>
  ),
});
