import { GraduationCap, LogOut } from "lucide-react";

import { auth, signOut } from "@/auth";
import { Sidebar } from "@/components/admin/sidebar";
import { Button } from "@/components/ui/button";

export default async function PanelLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <aside className="w-60 shrink-0 border-r bg-muted/30 p-4">
        <div className="flex items-center gap-2 px-2 pb-4">
          <GraduationCap className="h-5 w-5 text-primary" aria-hidden />
          <span className="font-medium">Degree admin</span>
        </div>
        <Sidebar />
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b px-6 py-3">
          <div className="text-sm text-muted-foreground">
            {session?.user?.email}
            {session?.user?.role ? (
              <span className="ml-2 rounded bg-muted px-1.5 py-0.5 text-xs">{session.user.role}</span>
            ) : null}
          </div>
          <form
            action={async () => {
              "use server";
              await signOut({ redirectTo: "/admin/login" });
            }}
          >
            <Button variant="ghost" size="sm" type="submit">
              <LogOut className="mr-1 h-4 w-4" aria-hidden />
              Sign out
            </Button>
          </form>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
