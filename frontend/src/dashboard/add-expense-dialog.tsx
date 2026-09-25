import { Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
import { useExpenses } from "@/hooks/use-expenses";
import { EXPENSE_CATEGORIES, type ExpenseCategory } from "@/types";
import { todayIso } from "@/utils/format";

export function AddExpenseDialog() {
  const { addExpense } = useExpenses();
  const [open, setOpen] = useState(false);
  const [merchant, setMerchant] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(todayIso());
  const [category, setCategory] = useState<ExpenseCategory | "auto">("auto");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    const value = Number(amount);
    if (!merchant.trim()) return setError("Merchant is required.");
    if (!Number.isFinite(value) || value <= 0) return setError("Enter an amount greater than 0.");
    if (!date) return setError("Pick a date.");

    setSaving(true);
    try {
      const result = await addExpense({ merchant: merchant.trim(), amount: Math.round(value * 100) / 100, date,
        category: category === "auto" ? undefined : category });
      toast.success(result.category_source === "ml"
        ? `Auto categorized as ${result.category}${result.category_confidence ? ` (${Math.round(result.category_confidence * 100)}% confidence)` : ""}`
        : `Expense added to ${result.category}`);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save expense."); return; }
    finally { setSaving(false); }
    setMerchant("");
    setAmount("");
    setError(null);
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="size-4" aria-hidden /> Add expense
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="font-display">Add expense</DialogTitle>
            <DialogDescription>Leave category empty to let the analyzer categorize it.</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="merchant">Merchant</Label>
            <Input
              id="merchant"
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              placeholder="Green Basket"
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                inputMode="decimal"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="42.50"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="category">Category</Label>
            <Select value={category} onValueChange={(v) => setCategory(v as ExpenseCategory | "auto")}>
              <SelectTrigger id="category">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto categorize</SelectItem>
                {EXPENSE_CATEGORIES.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => void submit()} disabled={saving}>{saving ? "Saving…" : "Save expense"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
