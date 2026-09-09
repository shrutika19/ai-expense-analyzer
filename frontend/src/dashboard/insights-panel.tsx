import { Link } from "@tanstack/react-router";
import { ArrowRight, Lightbulb, TrendingDown, TrendingUp } from "lucide-react";

import { EmptyBlock } from "@/common/states";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { buildInsights } from "@/dashboard/insights";
import type { Expense } from "@/types";

export function InsightsPanel({ expenses, limit = 3 }: { expenses: Expense[]; limit?: number }) {
  const insights = buildInsights(expenses).slice(0, limit);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-display flex items-center gap-2 text-base">
          <Lightbulb className="size-4 text-accent-foreground" aria-hidden />
          AI insights
        </CardTitle>
        <CardDescription>Generated summaries of your spending patterns</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {insights.length === 0 ? (
          <EmptyBlock title="Nothing to analyze yet" description="Add expenses to see insights." />
        ) : (
          insights.map((i) => {
            const Icon = i.tone === "up" ? TrendingUp : i.tone === "down" ? TrendingDown : Lightbulb;
            return (
              <div key={i.title} className="rounded-xl border border-border bg-muted/30 p-4">
                <div className="flex items-center gap-2">
                  <Icon className="size-4 text-muted-foreground" aria-hidden />
                  <p className="text-sm font-medium">{i.title}</p>
                </div>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{i.body}</p>
              </div>
            );
          })
        )}
        <Button asChild variant="outline" size="sm" className="w-full">
          <Link to="/insights">
            Ask a question <ArrowRight className="size-4" aria-hidden />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
