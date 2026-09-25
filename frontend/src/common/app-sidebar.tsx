import { Link, useRouterState } from "@tanstack/react-router";
import { BarChart3, LayoutDashboard, LogOut, MessageSquareText, Receipt, UploadCloud } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const items = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Expenses", url: "/expenses", icon: Receipt },
  { title: "Upload", url: "/upload", icon: UploadCloud },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "AI Insights", url: "/insights", icon: MessageSquareText },
] as const;

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const { user, logout } = useAuth();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-1.5">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary font-display text-sm font-bold text-primary-foreground">
            AE
          </span>
          {!collapsed && (
            <span className="font-display text-sm leading-tight font-semibold">
              Expense Analyzer
              <span className="block text-xs font-normal text-muted-foreground">
                AI spending copilot
              </span>
            </span>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url}
                    tooltip={item.title}
                  >
                    <Link to={item.url} className="flex items-center gap-2">
                      <item.icon className="size-4" aria-hidden />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <button className="flex items-center gap-2 px-2 text-sm text-muted-foreground hover:text-foreground" onClick={() => { logout(); window.location.assign("/login"); }}>
          <LogOut className="size-4" /> {!collapsed && `Sign out ${user?.email ?? ""}`}
        </button>
      </SidebarFooter>
    </Sidebar>
  );
}
