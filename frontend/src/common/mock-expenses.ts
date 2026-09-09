import type { Expense, ExpenseCategory } from "@/types";

/**
 * Deterministic mock dataset. Replaced by the FastAPI response later —
 * nothing here is persisted and no network call is made.
 */

const MERCHANTS: Record<ExpenseCategory, string[]> = {
  Groceries: ["Green Basket", "Freshmart", "Corner Grocer"],
  Dining: ["Noodle Bar", "Cafe Lumen", "Taco Yard", "Sunset Diner"],
  Transport: ["Metro Card", "RideNow", "City Parking", "Fuel Stop"],
  Housing: ["Rent — Maple St", "Home Repairs"],
  Utilities: ["PowerGrid Co", "AquaWorks", "FiberLink"],
  Shopping: ["Northline Apparel", "Deskly", "Bookhouse"],
  Health: ["Wellness Clinic", "PharmaPlus", "Peak Gym"],
  Entertainment: ["Cinema 8", "Vinyl Room", "Arcade Loft"],
  Travel: ["SkyHigh Air", "Harbor Hotel", "TrainLine"],
  Subscriptions: ["Streamly", "CloudDrive", "NewsDaily", "MusicBox"],
};

const WEIGHTS: [ExpenseCategory, number, number, number][] = [
  // category, weight, min amount, max amount
  ["Groceries", 18, 22, 140],
  ["Dining", 16, 9, 85],
  ["Transport", 12, 4, 70],
  ["Housing", 2, 60, 220],
  ["Utilities", 6, 45, 190],
  ["Shopping", 11, 18, 320],
  ["Health", 7, 15, 240],
  ["Entertainment", 9, 12, 95],
  ["Travel", 4, 120, 780],
  ["Subscriptions", 14, 5, 25],
];

function lcg(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
}

function pick<T>(arr: T[], r: number): T {
  return arr[Math.min(arr.length - 1, Math.floor(r * arr.length))] as T;
}

function buildExpenses(): Expense[] {
  const rand = lcg(20260909);
  const out: Expense[] = [];
  const now = new Date();
  const totalWeight = WEIGHTS.reduce((s, w) => s + w[1], 0);

  for (let back = 5; back >= 0; back--) {
    const base = new Date(now.getFullYear(), now.getMonth() - back, 1);
    const year = base.getFullYear();
    const month = base.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const maxDay = back === 0 ? now.getDate() : daysInMonth;
    // Later months drift slightly upward so trends are readable.
    const count = 20 + Math.floor(rand() * 6) + (5 - back);

    // One predictable rent charge each month keeps the trend readable.
    out.push({
      id: `rent-${year}-${month}`,
      date: `${year}-${String(month + 1).padStart(2, "0")}-01`,
      merchant: "Rent — Maple St",
      category: "Housing",
      amount: 1180,
    });

    for (let i = 0; i < count; i++) {
      let roll = rand() * totalWeight;
      let chosen = WEIGHTS[0] as [ExpenseCategory, number, number, number];
      for (const w of WEIGHTS) {
        roll -= w[1];
        if (roll <= 0) {
          chosen = w;
          break;
        }
      }
      const [category, , min, max] = chosen;
      const drift = 1 + (5 - back) * 0.03;
      const amount = Math.round((min + rand() * (max - min)) * drift * 100) / 100;
      const day = Math.max(1, Math.min(maxDay, Math.ceil(rand() * maxDay)));
      const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

      out.push({
        id: `exp-${year}${month}-${i}`,
        date: iso,
        merchant: pick(MERCHANTS[category], rand()),
        category,
        amount,
      });
    }
  }

  return out.sort((a, b) => b.date.localeCompare(a.date));
}

export const MOCK_EXPENSES: Expense[] = buildExpenses();
