import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/common/app-shell";
import { ChartSkeleton, ErrorBlock } from "@/common/states";
import { InsightsChat } from "@/dashboard/insights-chat";
import { InsightsPanel } from "@/dashboard/insights-panel";
import { useRangedExpenses } from "@/hooks/use-range";

export const Route = createFileRoute("/insights")({
  head: () => ({
    meta: [
      { title: "AI Insights — AI Expense Analyzer" },
      {
        name: "description",
        content:
          "Ask questions like 'Why did my expenses increase this month?' and read AI-generated explanations of your spending.",
      },
      { property: "og:title", content: "AI Insights — AI Expense Analyzer" },
      {
        property: "og:description",
        content: "A question-and-answer view over your spending data.",
      },
    ],
  }),
  component: InsightsPage,
});

function InsightsPage() {
  const { expenses, status, reload } = useRangedExpenses();

  if (status === "error") {
    return (
      <AppShell title="AI Insights">
        <ErrorBlock onRetry={reload} />
      </AppShell>
    );
  }

  return (
    <AppShell title="AI Insights" description="Ask questions about your spending">
      {status === "loading" ? (
        <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <ChartSkeleton height={640} />
          <ChartSkeleton height={400} />
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <InsightsChat expenses={expenses} />
          <InsightsPanel expenses={expenses} limit={4} />
        </div>
      )}
    </AppShell>
  );
}
