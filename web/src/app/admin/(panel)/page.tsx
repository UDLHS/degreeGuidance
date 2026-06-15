import Link from "next/link";

import { auth } from "@/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const CARDS = [
  { href: "/admin/ingestions", title: "Ingestions", desc: "Upload handbooks, review extractions, promote cutoffs." },
  { href: "/admin/aliases", title: "Aliases", desc: "Verify and correct OCR-label → course mappings." },
  { href: "/admin/courses", title: "Courses", desc: "Edit names, flags, and onboard new courses." },
];

export default async function DashboardPage() {
  const session = await auth();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-medium">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Signed in as {session?.user?.email}
          {session?.user?.role ? ` (${session.user.role})` : ""}.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CARDS.map((c) => (
          <Link key={c.href} href={c.href}>
            <Card className="h-full transition-colors hover:bg-accent/40">
              <CardHeader>
                <CardTitle className="text-base">{c.title}</CardTitle>
                <CardDescription>{c.desc}</CardDescription>
              </CardHeader>
              <CardContent>
                <span className="text-sm text-primary">Open →</span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      <p className="text-xs text-muted-foreground">
        Full metrics dashboard (charts, audit search) is Slice 3, deferred per masterplan §14.5.
      </p>
    </div>
  );
}
