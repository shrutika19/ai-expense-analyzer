import type { Expense } from "@/types";
import { averageExpense, byCategory, byMerchant, byMonth, monthOverMonth } from "@/utils/analytics";
import { formatMoney, formatPct } from "@/utils/format";

/**
 * Placeholder narrative generator. The real copy will come from the
 * FastAPI LLM/RAG endpoint — the shapes below match what the UI expects.
 */

export interface Insight {
  title: string;
  body: string;
  tone: "up" | "down" | "neutral";
}

export function buildInsights(expenses: Expense[]): Insight[] {
  if (expenses.length === 0) return [];
  const cats = byCategory(expenses);
  const months = byMonth(expenses);
  const mom = monthOverMonth(expenses);
  const top = cats[0];
  const merchant = byMerchant(expenses, 1)[0];
  const last = months[months.length - 1];

  const out: Insight[] = [];

  if (last) {
    out.push({
      title: mom >= 0 ? "Spending is trending up" : "Spending is trending down",
      body: `${last.label} totals ${formatMoney(last.total)} across ${last.count} transactions, ${formatPct(mom)} versus the previous month.`,
      tone: mom >= 0 ? "up" : "down",
    });
  }

  if (top) {
    out.push({
      title: `${top.category} dominates your budget`,
      body: `${top.category} accounts for ${top.share.toFixed(0)}% of spend (${formatMoney(top.total)} over ${top.count} transactions). Trimming it by 10% would save about ${formatMoney(top.total * 0.1)}.`,
      tone: "neutral",
    });
  }

  if (merchant) {
    out.push({
      title: `${merchant.merchant} is your top merchant`,
      body: `You spent ${formatMoney(merchant.total)} there across ${merchant.count} visits — an average of ${formatMoney(merchant.total / merchant.count, true)} per visit.`,
      tone: "neutral",
    });
  }

  out.push({
    title: "Transaction size is steady",
    body: `Your average transaction is ${formatMoney(averageExpense(expenses), true)}. Small recurring charges make up the bulk of your transaction count.`,
    tone: "neutral",
  });

  return out;
}

export const SUGGESTED_QUESTIONS = [
  "Why did my expenses increase this month?",
  "Which category should I cut first?",
  "Are there any unusual transactions?",
  "How does this month compare to my average?",
];

export function answerQuestion(question: string, expenses: Expense[]): string {
  const q = question.toLowerCase();
  const cats = byCategory(expenses);
  const months = byMonth(expenses);
  const last = months[months.length - 1];
  const prev = months[months.length - 2];
  const mom = monthOverMonth(expenses);
  const top = cats[0];

  if (expenses.length === 0) {
    return "There's no spending data in the selected range yet. Upload a statement or add an expense and I'll analyze it.";
  }

  if (q.includes("increase") || q.includes("why") || q.includes("compare")) {
    const driver = cats[0];
    return [
      `${last?.label ?? "This month"} came in at ${formatMoney(last?.total ?? 0)}${
        prev ? ` versus ${formatMoney(prev.total)} in ${prev.label} (${formatPct(mom)})` : ""
      }.`,
      driver
        ? `The largest driver is ${driver.category} at ${formatMoney(driver.total)} — roughly ${driver.share.toFixed(0)}% of total spend.`
        : "",
      "Most of the movement comes from a handful of larger one-off purchases rather than day-to-day activity.",
    ]
      .filter(Boolean)
      .join(" ");
  }

  if (q.includes("cut") || q.includes("save") || q.includes("reduce")) {
    const second = cats[1];
    return [
      top
        ? `Start with ${top.category}: ${formatMoney(top.total)} over ${top.count} transactions. A 15% trim frees up about ${formatMoney(top.total * 0.15)}.`
        : "",
      second
        ? `${second.category} is the next lever at ${formatMoney(second.total)}, and it's mostly discretionary.`
        : "",
    ]
      .filter(Boolean)
      .join(" ");
  }

  if (q.includes("unusual") || q.includes("anomal") || q.includes("outlier")) {
    const avg = averageExpense(expenses);
    const outliers = expenses.filter((e) => e.amount > avg * 4).slice(0, 3);
    if (outliers.length === 0) {
      return `Nothing stands out — every transaction sits within a normal band around your ${formatMoney(avg, true)} average.`;
    }
    return `${outliers.length} transaction(s) sit far above your ${formatMoney(avg, true)} average: ${outliers
      .map((e) => `${e.merchant} (${formatMoney(e.amount)})`)
      .join(", ")}. Worth a quick review.`;
  }

  return `Across the selected range you spent ${formatMoney(expenses.reduce((s, e) => s + e.amount, 0))} over ${expenses.length} transactions, averaging ${formatMoney(averageExpense(expenses), true)} each.${
    top ? ` ${top.category} leads at ${top.share.toFixed(0)}% of the total.` : ""
  }`;
}
