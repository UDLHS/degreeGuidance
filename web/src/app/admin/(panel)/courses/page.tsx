"use client";

import { useCallback, useEffect, useState } from "react";
import { Pencil, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Course = {
  course_code: string;
  course_number: string | null;
  university_id: number;
  university_code: string | null;
  name_en: string;
  degree_type: string | null;
  duration_years: number | null;
  selection_basis: string;
  requires_aptitude_test: boolean;
  first_intake_year: number | null;
  is_active: boolean;
};

type University = { university_id: number; university_code: string | null };

type Form = {
  course_code: string;
  university_id: string;
  course_number: string;
  name_en: string;
  selection_basis: string;
  requires_aptitude_test: boolean;
  duration_years: string;
  degree_type: string;
  first_intake_year: string;
  is_active: boolean;
};

const EMPTY: Form = {
  course_code: "",
  university_id: "",
  course_number: "",
  name_en: "",
  selection_basis: "district_quota",
  requires_aptitude_test: false,
  duration_years: "",
  degree_type: "",
  first_intake_year: "",
  is_active: true,
};

export default function CoursesPage() {
  const [items, setItems] = useState<Course[]>([]);
  const [total, setTotal] = useState(0);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [active, setActive] = useState("all");
  const [basis, setBasis] = useState("all");
  const [open, setOpen] = useState(false);
  const [editCode, setEditCode] = useState<string | null>(null);
  const [form, setForm] = useState<Form>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [dialogErr, setDialogErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const p = new URLSearchParams({ limit: "200" });
    if (q.trim()) p.set("q", q.trim());
    if (active !== "all") p.set("is_active", active);
    if (basis !== "all") p.set("selection_basis", basis);
    const res = await fetch(`/api/bff/admin/courses?${p.toString()}`, { cache: "no-store" });
    if (res.ok) {
      const d = await res.json();
      setItems(d.items ?? []);
      setTotal(d.total ?? 0);
    }
    setLoading(false);
  }, [q, active, basis]);

  useEffect(() => {
    load();
  }, [load]);

  // Build the university dropdown from an unfiltered course fetch (no universities endpoint).
  useEffect(() => {
    (async () => {
      const res = await fetch("/api/bff/admin/courses?limit=200", { cache: "no-store" });
      if (!res.ok) return;
      const d = await res.json();
      const seen = new Map<number, University>();
      for (const c of d.items ?? []) {
        if (!seen.has(c.university_id))
          seen.set(c.university_id, { university_id: c.university_id, university_code: c.university_code });
      }
      setUniversities(
        Array.from(seen.values()).sort((a, b) =>
          (a.university_code ?? "").localeCompare(b.university_code ?? ""),
        ),
      );
    })();
  }, []);

  function openCreate() {
    setEditCode(null);
    setForm(EMPTY);
    setDialogErr(null);
    setOpen(true);
  }

  function openEdit(c: Course) {
    setEditCode(c.course_code);
    setForm({
      course_code: c.course_code,
      university_id: String(c.university_id),
      course_number: c.course_number ?? "",
      name_en: c.name_en,
      selection_basis: c.selection_basis,
      requires_aptitude_test: c.requires_aptitude_test,
      duration_years: c.duration_years != null ? String(c.duration_years) : "",
      degree_type: c.degree_type ?? "",
      first_intake_year: c.first_intake_year != null ? String(c.first_intake_year) : "",
      is_active: c.is_active,
    });
    setDialogErr(null);
    setOpen(true);
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setDialogErr(null);
    const isCreate = editCode === null;
    const common: Record<string, unknown> = {
      name_en: form.name_en,
      selection_basis: form.selection_basis,
      requires_aptitude_test: form.requires_aptitude_test,
      degree_type: form.degree_type || null,
      is_active: form.is_active,
    };
    if (form.duration_years !== "") common.duration_years = Number(form.duration_years);
    if (form.first_intake_year !== "") common.first_intake_year = Number(form.first_intake_year);

    let res: Response;
    if (isCreate) {
      res = await fetch("/api/bff/admin/courses", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          ...common,
          course_code: form.course_code.trim().toUpperCase(),
          university_id: Number(form.university_id),
          course_number: form.course_number || null,
        }),
      });
    } else {
      res = await fetch(`/api/bff/admin/courses/${editCode}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(common),
      });
    }
    const data = await res.json().catch(() => null);
    setSaving(false);
    if (res.ok) {
      setOpen(false);
      load();
    } else {
      setDialogErr(typeof data?.detail === "string" ? data.detail : `Failed (${res.status}).`);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium">Courses</h1>
          <p className="text-sm text-muted-foreground">
            {total} courses. Edit names and flags, or add a new course (new-handbook onboarding).
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-1 h-4 w-4" aria-hidden /> Add course
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search code or name…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={active} onValueChange={setActive}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Active" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="true">Active</SelectItem>
            <SelectItem value="false">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Select value={basis} onValueChange={setBasis}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Selection basis" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All bases</SelectItem>
            <SelectItem value="district_quota">district_quota</SelectItem>
            <SelectItem value="all_island_merit">all_island_merit</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="ghost" size="sm" onClick={load} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Univ</TableHead>
              <TableHead>Basis</TableHead>
              <TableHead>Aptitude</TableHead>
              <TableHead>Active</TableHead>
              <TableHead className="text-right">Edit</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.length === 0 && !loading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-sm text-muted-foreground">
                  No courses match.
                </TableCell>
              </TableRow>
            ) : (
              items.map((c) => (
                <TableRow key={c.course_code}>
                  <TableCell className="font-mono text-xs">{c.course_code}</TableCell>
                  <TableCell className="max-w-xs truncate text-sm">{c.name_en}</TableCell>
                  <TableCell className="text-xs">{c.university_code ?? c.university_id}</TableCell>
                  <TableCell className="text-xs">
                    {c.selection_basis === "all_island_merit" ? "AIM" : "DQ"}
                  </TableCell>
                  <TableCell>{c.requires_aptitude_test ? "yes" : "—"}</TableCell>
                  <TableCell>
                    <span
                      className={
                        c.is_active
                          ? "rounded-md bg-green-100 px-2 py-0.5 text-xs text-green-800"
                          : "rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                      }
                    >
                      {c.is_active ? "active" : "inactive"}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(c)} title="Edit">
                      <Pencil className="h-4 w-4" aria-hidden />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <form onSubmit={submit}>
            <DialogHeader>
              <DialogTitle>{editCode === null ? "Add course" : `Edit ${editCode}`}</DialogTitle>
              <DialogDescription>
                {editCode === null
                  ? "Add a course at an existing university (set its * and # flags from the handbook)."
                  : "Edit the name and admission flags. Structural keys are not editable here."}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-4">
              {editCode === null ? (
                <div className="flex gap-3">
                  <div className="w-32 space-y-1.5">
                    <Label htmlFor="code">Course code</Label>
                    <Input
                      id="code"
                      value={form.course_code}
                      onChange={(e) => setForm({ ...form, course_code: e.target.value })}
                      placeholder="262A"
                      required
                    />
                  </div>
                  <div className="flex-1 space-y-1.5">
                    <Label htmlFor="univ">University</Label>
                    <Select
                      value={form.university_id}
                      onValueChange={(v) => setForm({ ...form, university_id: v })}
                    >
                      <SelectTrigger id="univ">
                        <SelectValue placeholder="Select university" />
                      </SelectTrigger>
                      <SelectContent>
                        {universities.map((u) => (
                          <SelectItem key={u.university_id} value={String(u.university_id)}>
                            {u.university_code ?? u.university_id}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="w-24 space-y-1.5">
                    <Label htmlFor="num">Number</Label>
                    <Input
                      id="num"
                      value={form.course_number}
                      onChange={(e) => setForm({ ...form, course_number: e.target.value })}
                      placeholder="262"
                    />
                  </div>
                </div>
              ) : null}
              <div className="space-y-1.5">
                <Label htmlFor="name">Name (English)</Label>
                <Input
                  id="name"
                  value={form.name_en}
                  onChange={(e) => setForm({ ...form, name_en: e.target.value })}
                  required
                />
              </div>
              <div className="flex gap-3">
                <div className="flex-1 space-y-1.5">
                  <Label htmlFor="basis2">Selection basis</Label>
                  <Select
                    value={form.selection_basis}
                    onValueChange={(v) => setForm({ ...form, selection_basis: v })}
                  >
                    <SelectTrigger id="basis2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="district_quota">district_quota</SelectItem>
                      <SelectItem value="all_island_merit">all_island_merit</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="w-28 space-y-1.5">
                  <Label htmlFor="dur">Duration (yrs)</Label>
                  <Input
                    id="dur"
                    type="number"
                    step="0.5"
                    value={form.duration_years}
                    onChange={(e) => setForm({ ...form, duration_years: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-wrap gap-4">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.requires_aptitude_test}
                    onChange={(e) => setForm({ ...form, requires_aptitude_test: e.target.checked })}
                  />
                  Requires aptitude test (#)
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  />
                  Active
                </label>
              </div>
              {dialogErr ? <p className="text-sm text-destructive">{dialogErr}</p> : null}
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
