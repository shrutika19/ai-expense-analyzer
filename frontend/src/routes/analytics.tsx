import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/common/app-shell";
import { ChartSkeleton, EmptyBlock, ErrorBlock } from "@/common/states";
import {
  LazyCategoryBarChart,
  LazyMerchantChart,
  LazyMomChart,
  LazyMonthlyTrendChart,
} from "@/dashboard/lazy-charts";
import { useRangedExpenses } from "@/hooks/use-range";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — AI Expense Analyzer" },
      {
        name: "description",
        content:
          "Deeper spending analysis: trends over time, category comparison, top merchants and month-over-month change.",
      },
      { property: "og:title", content: "Analytics — AI Expense Analyzer" },
      {
        property: "og:description",
        content: "Charts for spend over time, categories, merchants and monthly change.",
      },
    ],
  }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const { expenses, status, reload } = useRangedExpenses();

  if (status === "error") {
    return (
      <AppShell title="Analytics">
        <ErrorBlock onRetry={reload} />
      </AppShell>
    );
  }

  return (
    <AppShell title="Analytics" description="A closer look at your spending patterns">
      {status === "loading" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <ChartSkeleton key={i} height={360} />
          ))}
        </div>
      ) : expenses.length === 0 ? (
        <EmptyBlock title="No data in this range" description="Try a wider date range." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <LazyMonthlyTrendChart expenses={expenses} />
          <LazyCategoryBarChart expenses={expenses} />
          <LazyMerchantChart expenses={expenses} />
          <LazyMomChart expenses={expenses} />
        </div>
      )}
    </AppShell>
  );
}
