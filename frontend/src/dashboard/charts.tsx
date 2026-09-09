import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Expense } from "@/types";
import { byCategory, byMerchant, byMonth } from "@/utils/analytics";
import { formatMoney } from "@/utils/format";

const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

const axisProps = {
  stroke: "var(--muted-foreground)",
  fontSize: 12,
  tickLine: false,
  axisLine: false,
} as const;

function tooltipStyles() {
  return {
    contentStyle: {
      background: "var(--popover)",
      border: "1px solid var(--border)",
      borderRadius: "0.6rem",
      fontSize: "0.8rem",
      color: "var(--popover-foreground)",
    },
    labelStyle: { color: "var(--popover-foreground)" },
    itemStyle: { color: "var(--popover-foreground)" },
  };
}

function ChartCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-display text-base">{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent className="h-70 pr-2">{children}</CardContent>
    </Card>
  );
}

export function CategoryChart({ expenses }: { expenses: Expense[] }) {
  const data = byCategory(expenses).slice(0, 6);
  return (
    <ChartCard title="Spend by category" description="Where the money goes">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="total"
            nameKey="category"
            innerRadius={58}
            outerRadius={96}
            paddingAngle={2}
            stroke="var(--background)"
          >
            {data.map((entry, i) => (
              <Cell key={entry.category} fill={PALETTE[i % PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => formatMoney(v)} {...tooltipStyles()} />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            iconType="circle"
            wrapperStyle={{ fontSize: "0.78rem", color: "var(--muted-foreground)" }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function MonthlyTrendChart({ expenses }: { expenses: Expense[] }) {
  const data = byMonth(expenses);
  return (
    <ChartCard title="Monthly trend" description="Total spend per month">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ left: -14, right: 8, top: 8 }}>
          <defs>
            <linearGradient id="spendFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.45} />
              <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <XAxis dataKey="label" {...axisProps} />
          <YAxis {...axisProps} tickFormatter={(v: number) => formatMoney(v)} width={64} />
          <Tooltip formatter={(v: number) => formatMoney(v)} {...tooltipStyles()} />
          <Area
            type="monotone"
            dataKey="total"
            name="Spend"
            stroke="var(--chart-1)"
            strokeWidth={2}
            fill="url(#spendFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function CategoryBarChart({ expenses }: { expenses: Expense[] }) {
  const data = byCategory(expenses);
  return (
    <ChartCard title="Category comparison" description="Total per category">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: -14, right: 8, top: 8 }}>
          <XAxis dataKey="category" {...axisProps} interval={0} angle={-25} textAnchor="end" height={60} />
          <YAxis {...axisProps} tickFormatter={(v: number) => formatMoney(v)} width={64} />
          <Tooltip cursor={{ fill: "var(--muted)" }} formatter={(v: number) => formatMoney(v)} {...tooltipStyles()} />
          <Bar dataKey="total" name="Spend" radius={[6, 6, 0, 0]} fill="var(--chart-2)" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function MerchantChart({ expenses }: { expenses: Expense[] }) {
  const data = byMerchant(expenses, 7);
  return (
    <ChartCard title="Top merchants" description="Highest total spend">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 40, right: 16 }}>
          <XAxis type="number" {...axisProps} tickFormatter={(v: number) => formatMoney(v)} />
          <YAxis type="category" dataKey="merchant" {...axisProps} width={110} />
          <Tooltip cursor={{ fill: "var(--muted)" }} formatter={(v: number) => formatMoney(v)} {...tooltipStyles()} />
          <Bar dataKey="total" name="Spend" radius={[0, 6, 6, 0]} fill="var(--chart-4)" />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function MomChart({ expenses }: { expenses: Expense[] }) {
  const months = byMonth(expenses);
  const data = months.map((m, i) => {
    const prev = months[i - 1]?.total ?? 0;
    const change = prev ? ((m.total - prev) / prev) * 100 : 0;
    return { label: m.label, change: Math.round(change * 10) / 10 };
  });
  return (
    <ChartCard title="Month-over-month change" description="Percent difference vs previous month">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: -18, right: 8, top: 8 }}>
          <XAxis dataKey="label" {...axisProps} />
          <YAxis {...axisProps} tickFormatter={(v: number) => `${v}%`} width={56} />
          <Tooltip cursor={{ fill: "var(--muted)" }} formatter={(v: number) => `${v}%`} {...tooltipStyles()} />
          <Bar dataKey="change" name="Change" radius={[6, 6, 6, 6]}>
            {data.map((d) => (
              <Cell
                key={d.label}
                fill={d.change >= 0 ? "var(--chart-5)" : "var(--chart-3)"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
