"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Bot,
  Database,
  FileText,
  Grid3x3,
  LayoutDashboard,
  ListChecks,
  MessagesSquare,
  ShieldCheck,
  Tags,
  Upload,
} from "lucide-react";

import { cn } from "@/lib/utils";

const NAV = [
  { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/ingestions", label: "Ingestions", icon: Upload },
  { href: "/admin/cutoffs", label: "Cutoffs", icon: Grid3x3 },
  { href: "/admin/conversations", label: "Conversations", icon: MessagesSquare },
  { href: "/admin/agent", label: "AI Advisor", icon: Bot },
  { href: "/admin/aliases", label: "Aliases", icon: Tags },
  { href: "/admin/courses", label: "Courses", icon: BookOpen },
  { href: "/admin/requirements", label: "Subject Rules", icon: ListChecks },
  { href: "/admin/factsheets", label: "Factsheets", icon: FileText },
  { href: "/admin/knowledge", label: "Knowledge", icon: Database },
  { href: "/admin/admins", label: "Admins", icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <nav className="flex flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground",
              active && "bg-accent font-medium text-foreground",
            )}
          >
            <Icon className="h-4 w-4" aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
