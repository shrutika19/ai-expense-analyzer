import { ArrowDownRight, ArrowUpRight, Receipt, Tag, TrendingUp, Wallet } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { Expense } from "@/types";
import { averageExpense, byCategory, monthOverMonth, totalSpend } from "@/utils/analytics";
import { formatMoney, formatNumber, formatPct } from "@/utils/format";

export function KpiCards({ expenses, loading }: { expenses: Expense[]; loading?: boolean }) {
  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28 rounded-xl" />
        ))}
      </div>
    );
  }

  const top = byCategory(expenses)[0];
  const mom = monthOverMonth(expenses);

  const cards = [
    {
      label: "Total expenses",
      value: formatMoney(totalSpend(expenses)),
      hint: "Across the selected range",
      icon: Wallet,
      delta: mom,
    },
    {
      label: "Average expense",
      value: formatMoney(averageExpense(expenses), true),
      hint: "Per transaction",
      icon: TrendingUp,
    },
    {
      label: "Transactions",
      value: formatNumber(expenses.length),
      hint: "Recorded entries",
      icon: Receipt,
    },
    {
      label: "Top category",
      value: top ? top.category : "—",
      hint: top ? `${formatMoney(top.total)} · ${top.share.toFixed(0)}% of spend` : "No data",
      icon: Tag,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((c) => {
        const Icon = c.icon;
        const up = (c.delta ?? 0) > 0;
        return (
          <Card key={c.label} className="overflow-hidden">
            <CardContent className="space-y-2 p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                  {c.label}
                </span>
                <Icon className="size-4 text-muted-foreground" aria-hidden />
              </div>
              <p className="font-display truncate text-2xl font-semibold tracking-tight">
                {c.value}
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {c.delta !== undefined && c.delta !== 0 ? (
                  <span
                    className={
                      up
                        ? "inline-flex items-center gap-0.5 rounded-full bg-destructive/10 px-1.5 py-0.5 font-medium text-destructive"
                        : "inline-flex items-center gap-0.5 rounded-full bg-accent/15 px-1.5 py-0.5 font-medium text-accent-foreground"
                    }
                  >
                    {up ? (
                      <ArrowUpRight className="size-3" aria-hidden />
                    ) : (
                      <ArrowDownRight className="size-3" aria-hidden />
                    )}
                    {formatPct(c.delta)}
                  </span>
                ) : null}
                <span className="truncate">{c.hint}</span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
