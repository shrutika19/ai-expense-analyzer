import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, Search, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { EmptyBlock, LoadingBlock } from "@/common/states";
import { AddExpenseDialog } from "@/dashboard/add-expense-dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
import { useExpenses } from "@/hooks/use-expenses";
import { EXPENSE_CATEGORIES, type Expense } from "@/types";
import { formatDate, formatMoney } from "@/utils/format";

type SortKey = "date" | "merchant" | "category" | "amount";
const PAGE_SIZE = 10;

function SortHeader({
  label,
  k,
  right,
  active,
  asc,
  onToggle,
}: {
  label: string;
  k: SortKey;
  right?: boolean;
  active: boolean;
  asc: boolean;
  onToggle: (key: SortKey) => void;
}) {
  return (
    <TableHead className={right ? "text-right" : undefined}>
      <button
        type="button"
        onClick={() => onToggle(k)}
        className={`inline-flex items-center gap-1 text-xs font-medium tracking-wide uppercase transition-colors hover:text-foreground ${
          active ? "text-foreground" : "text-muted-foreground"
        }`}
      >
        {label}
        {active ? (
          asc ? (
            <ArrowUp className="size-3" aria-hidden />
          ) : (
            <ArrowDown className="size-3" aria-hidden />
          )
        ) : null}
      </button>
    </TableHead>
  );
}

export function ExpensesTable({ expenses, loading }: { expenses: Expense[]; loading?: boolean }) {
  const { deleteExpense } = useExpenses();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [asc, setAsc] = useState(false);
  const [page, setPage] = useState(0);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = expenses.filter((e) => {
      const matchesQuery =
        !q || e.merchant.toLowerCase().includes(q) || e.category.toLowerCase().includes(q);
      const matchesCat = category === "all" || e.category === category;
      return matchesQuery && matchesCat;
    });
    const dir = asc ? 1 : -1;
    return [...filtered].sort((a, b) => {
      if (sortKey === "amount") return (a.amount - b.amount) * dir;
      return String(a[sortKey]).localeCompare(String(b[sortKey])) * dir;
    });
  }, [expenses, query, category, sortKey, asc]);

  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const current = Math.min(page, pageCount - 1);
  const paged = rows.slice(current * PAGE_SIZE, current * PAGE_SIZE + PAGE_SIZE);

  function toggleSort(key: SortKey) {
    if (key === sortKey) setAsc((v) => !v);
    else {
      setSortKey(key);
      setAsc(key !== "date" && key !== "amount");
    }
    setPage(0);
  }

  return (
    <Card>
      <CardContent className="space-y-4 p-4 md:p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-50 flex-1">
            <Search
              className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden
            />
            <Input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(0);
              }}
              placeholder="Search merchant or category"
              className="pl-9"
              aria-label="Search expenses"
            />
          </div>
          <Select
            value={category}
            onValueChange={(v) => {
              setCategory(v);
              setPage(0);
            }}
          >
            <SelectTrigger className="w-43" aria-label="Filter by category">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {EXPENSE_CATEGORIES.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <AddExpenseDialog />
        </div>

        {loading ? (
          <LoadingBlock rows={6} />
        ) : paged.length === 0 ? (
          <EmptyBlock
            title="No matching expenses"
            description="Try a different search term or clear the category filter."
          />
        ) : (
          <div className="overflow-x-auto rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <SortHeader label="Date" k="date" active={sortKey === "date"} asc={asc} onToggle={toggleSort} />
                  <SortHeader label="Merchant" k="merchant" active={sortKey === "merchant"} asc={asc} onToggle={toggleSort} />
                  <SortHeader label="Category" k="category" active={sortKey === "category"} asc={asc} onToggle={toggleSort} />
                  <TableHead>Source</TableHead>
                  <SortHeader label="Amount" k="amount" right active={sortKey === "amount"} asc={asc} onToggle={toggleSort} />
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {paged.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell className="whitespace-nowrap text-muted-foreground">
                      {formatDate(e.date)}
                    </TableCell>
                    <TableCell className="font-medium">{e.merchant}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{e.category}</Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {e.category_source === "ml" ? "Auto categorized" : "Manual"}
                    </TableCell>
                    <TableCell className="text-right font-semibold tabular-nums">
                      {formatMoney(e.amount, true)}
                    </TableCell>
                    <TableCell>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`Delete ${e.merchant} expense`}
                          >
                            <Trash2 className="size-4 text-muted-foreground" aria-hidden />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete this expense?</AlertDialogTitle>
                            <AlertDialogDescription>
                              {e.merchant} · {formatMoney(e.amount, true)} on {formatDate(e.date)}.
                              This removes it from the current session.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => {
                                deleteExpense(e.id);
                                toast.success("Expense deleted");
                              }}
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}

        {!loading && rows.length > 0 ? (
          <div className="flex items-center justify-between gap-3 text-sm text-muted-foreground">
            <span>
              {rows.length} result{rows.length === 1 ? "" : "s"} · page {current + 1} of {pageCount}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={current === 0}
                onClick={() => setPage(current - 1)}
              >
                <ChevronLeft className="size-4" aria-hidden /> Prev
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={current >= pageCount - 1}
                onClick={() => setPage(current + 1)}
              >
                Next <ChevronRight className="size-4" aria-hidden />
              </Button>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
