'use client';

import { Command, HdmiPort, History, Settings, Workflow } from 'lucide-react';
import * as React from 'react';

import { NavUser } from '@/components/nav-user';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  // SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { Link, useRouterState } from '@tanstack/react-router';

// This is sample data
const data = {
  user: {
    name: 'shadcn',
    email: 'm@example.com',
    avatar: '/avatars/shadcn.jpg',
  },
  navMain: [
    {
      title: 'My Flows',
      url: '/flows',
      icon: Workflow,
      isActive: true,
    },
    {
      title: 'Connectors',
      url: '/connectors',
      icon: HdmiPort,
      isActive: false,
    },
    {
      title: 'Workflow Runs',
      url: '/runs',
      icon: History,
      isActive: false,
    },
    {
      title: 'Settings',
      url: '/settings',
      icon: Settings,
      isActive: false,
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const routerState = useRouterState();
  const { state } = useSidebar()

  const activeItem = React.useMemo(() => {
    return data.navMain.find(item => routerState.location.pathname === item.url) || data.navMain[0];
  }, [routerState.location.pathname]);

  return (
    <Sidebar collapsible="icon" {...props}>
      {/* <Sidebar collapsible="none" className="!w-[calc(var(--sidebar-width-icon)_+_1px)] border-r"> */}
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild className="md:h-8 md:p-0">
              <a href="#">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Command className="size-4" />
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent className="px-1.5 md:px-0">
            <SidebarMenu>
              {data.navMain.map(item => (
                <SidebarMenuItem key={item.title}>
                  <Link to={item.url}>
                    <SidebarMenuButton
                      tooltip={{ children: item.title, hidden: state === 'expanded' }}
                      isActive={activeItem?.title === item.title}
                      className="px-2.5 md:px-2 cursor-pointer"
                    >
                      <item.icon />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      {/* </Sidebar> */}
    </Sidebar>
  );
}
