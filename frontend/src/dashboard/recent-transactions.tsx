import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyBlock } from "@/common/states";
import type { Expense } from "@/types";
import { recent } from "@/utils/analytics";
import { formatDate, formatMoney } from "@/utils/format";

export function RecentTransactions({ expenses }: { expenses: Expense[] }) {
  const rows = recent(expenses, 7);
  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-display text-base">Recent transactions</CardTitle>
        <CardDescription>Latest activity in this range</CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <EmptyBlock title="No transactions yet" />
        ) : (
          <ul className="divide-y divide-border">
            {rows.map((e) => (
              <li key={e.id} className="flex items-center justify-between gap-3 py-2.5">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{e.merchant}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(e.date)}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <Badge variant="secondary" className="hidden sm:inline-flex">
                    {e.category}
                  </Badge>
                  <span className="text-sm font-semibold tabular-nums">
                    {formatMoney(e.amount, true)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
