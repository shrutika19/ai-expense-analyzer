import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/common/app-shell";
import { ChartSkeleton, ErrorBlock, SectionHeading } from "@/common/states";
import { LazyCategoryChart, LazyMonthlyTrendChart } from "@/dashboard/lazy-charts";
import { InsightsPanel } from "@/dashboard/insights-panel";
import { KpiCards } from "@/dashboard/kpi-cards";
import { RecentTransactions } from "@/dashboard/recent-transactions";
import { useRangedExpenses } from "@/hooks/use-range";
import { useAnalyticsSummary } from "@/hooks/use-analytics-summary";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — AI Expense Analyzer" },
      {
        name: "description",
        content:
          "Track total spend, average expense, transaction volume and top categories with AI-generated spending insights.",
      },
      { property: "og:title", content: "Dashboard — AI Expense Analyzer" },
      {
        property: "og:description",
        content: "KPI cards, category and monthly charts, and AI insights for your spending.",
      },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  const { expenses, status, reload } = useRangedExpenses();
  const loading = status === "loading";
  const { summary, loading: summaryLoading } = useAnalyticsSummary();

  return (
    <AppShell title="Dashboard" description="Your spending at a glance">
      {status === "error" ? (
        <ErrorBlock onRetry={reload} />
      ) : (
        <>
          <KpiCards expenses={expenses} summary={summary} loading={loading || summaryLoading} />

          <SectionHeading title="Trends" description="How spending moves across the range" />
          <div className="grid gap-4 lg:grid-cols-2">
            {loading ? (
              <>
                <ChartSkeleton height={360} />
                <ChartSkeleton height={360} />
              </>
            ) : (
              <>
                <LazyMonthlyTrendChart expenses={expenses} />
                <LazyCategoryChart expenses={expenses} />
              </>
            )}
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {loading ? (
              <>
                <ChartSkeleton height={320} />
                <ChartSkeleton height={320} />
              </>
            ) : (
              <>
                <InsightsPanel expenses={expenses} />
                <RecentTransactions expenses={expenses} />
              </>
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}
