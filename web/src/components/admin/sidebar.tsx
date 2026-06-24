"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, FileText, LayoutDashboard, ListChecks, Tags, Upload } from "lucide-react";

import { cn } from "@/lib/utils";

const NAV = [
  { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/ingestions", label: "Ingestions", icon: Upload },
  { href: "/admin/aliases", label: "Aliases", icon: Tags },
  { href: "/admin/courses", label: "Courses", icon: BookOpen },
  { href: "/admin/requirements", label: "Subject Rules", icon: ListChecks },
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
      <p className="mt-3 px-3 py-1 text-xs text-muted-foreground/70">Slice 2 — later</p>
      <span className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground/40">
        <FileText className="h-4 w-4" aria-hidden />
        Factsheets
      </span>
    </nav>
  );
}
