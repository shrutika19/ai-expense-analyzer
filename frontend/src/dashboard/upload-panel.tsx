import { CheckCircle2, FileWarning, Loader2, UploadCloud, X } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { ParsedRow, UploadStatus } from "@/types";
import { formatMoney } from "@/utils/format";
import { useExpenseUpload } from "@/hooks/use-expense-upload";


const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPTED = [".csv", ".json"];

function parseCsv(text: string): ParsedRow[] {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const header = (lines[0] ?? "").split(",").map((h) => h.trim().toLowerCase());
  const idx = (name: string) => header.indexOf(name);
  const cols = {
    date: idx("date"),
    merchant: idx("merchant"),
    category: idx("category"),
    amount: idx("amount"),
  };
  if (Object.values(cols).some((c) => c < 0)) {
    throw new Error("CSV needs date, merchant, category and amount columns.");
  }
  return lines.slice(1).map((line, i) => {
    const parts = line.split(",");
    const amount = Number((parts[cols.amount] ?? "").trim());
    if (!Number.isFinite(amount)) throw new Error(`Row ${i + 2} has an invalid amount.`);
    return {
      date: (parts[cols.date] ?? "").trim(),
      merchant: (parts[cols.merchant] ?? "").trim(),
      category: (parts[cols.category] ?? "").trim(),
      amount,
    };
  });
}

function parseJson(text: string): ParsedRow[] {
  const data: unknown = JSON.parse(text);
  if (!Array.isArray(data)) throw new Error("JSON must be an array of expense objects.");
  return data.map((raw, i) => {
    const row = raw as Record<string, unknown>;
    const amount = Number(row["amount"]);
    if (!Number.isFinite(amount)) throw new Error(`Item ${i + 1} has an invalid amount.`);
    return {
      date: String(row["date"] ?? ""),
      merchant: String(row["merchant"] ?? ""),
      category: String(row["category"] ?? ""),
      amount,
    };
  });
}

export function UploadPanel() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState<string | null>(null);
  const [rows, setRows] = useState<ParsedRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const { upload_file } = useExpenseUpload();

  function reset() {
    setStatus("idle");
    setProgress(0);
    setFileName(null);
    setRows([]);
    setError(null);
  }

async function handleFile(file: File) {
  setFileName(file.name);
  setRows([]);
  setError(null);
  setStatus("validating");
  setProgress(0);

  const ext = file.name
    .slice(file.name.lastIndexOf("."))
    .toLowerCase();

  if (!ACCEPTED.includes(ext)) {
    setStatus("error");
    setError("Only .csv and .json files are supported.");
    return;
  }

  if (file.size > MAX_BYTES) {
    setStatus("error");
    setError("File is larger than 5 MB.");
    return;
  }

  try {
    const text = await file.text();

    const parsed =
      ext === ".csv"
        ? parseCsv(text)
        : parseJson(text);

    if (parsed.length === 0) {
      throw new Error("The file has no rows.");
    }

    setRows(parsed);
  } catch (e) {
    setStatus("error");
    setError(
      e instanceof Error
        ? e.message
        : "We couldn't read that file.",
    );
    return;
  }

  setStatus("uploading");
  setProgress(25);

  try {
    const response = await upload_file(file);

    if (!response) {
      setStatus("error");
      setError("Failed to import expenses.");
      setProgress(0);
      return;
    }

    setProgress(100);
    setStatus("success");

    toast.success(
      `${response.imported_count} expenses imported successfully.`,
    );
  } catch (e) {
    setStatus("error");
    setError(
      e instanceof Error
        ? e.message
        : "Failed to import expenses.",
    );
    setProgress(0);
  }
}

  const busy = status === "validating" || status === "uploading";

  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle className="font-display text-base">Upload a statement</CardTitle>
          <CardDescription>
            CSV or JSON, up to 5 MB. Files are validated in the browser only — nothing is sent
            anywhere yet.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              const file = e.dataTransfer.files?.[0];
              if (file) void handleFile(file);
            }}
            className={cn(
              "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors",
              dragging
                ? "border-primary bg-primary/5"
                : "border-border bg-muted/30 hover:border-primary/50",
            )}
          >
            <UploadCloud className="size-8 text-muted-foreground" aria-hidden />
            <div>
              <p className="text-sm font-medium">Drop your file here, or click to browse</p>
              <p className="text-xs text-muted-foreground">
                Expected columns: date, merchant, category, amount
              </p>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept=".csv,.json,text/csv,application/json"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void handleFile(file);
                e.target.value = "";
              }}
            />
          </div>

          {fileName ? (
            <div className="space-y-3 rounded-xl border border-border p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2">
                  {status === "success" ? (
                    <CheckCircle2 className="size-4 text-accent-foreground" aria-hidden />
                  ) : status === "error" ? (
                    <FileWarning className="size-4 text-destructive" aria-hidden />
                  ) : (
                    <Loader2 className="size-4 animate-spin text-muted-foreground" aria-hidden />
                  )}
                  <span className="truncate text-sm font-medium">{fileName}</span>
                </div>
                <Button variant="ghost" size="icon" onClick={reset} aria-label="Clear file">
                  <X className="size-4" aria-hidden />
                </Button>
              </div>

              {busy ? <Progress value={status === "uploading" ? progress : 8} /> : null}

              <p
                className={cn(
                  "text-sm",
                  status === "error" ? "text-destructive" : "text-muted-foreground",
                )}
              >
                {status === "validating" && "Checking file type and contents…"}
                {status === "uploading" && `Processing… ${progress}%`}
                {status === "success" && `${rows.length} rows validated and ready.`}
                {status === "error" && error}
              </p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-display text-base">Preview</CardTitle>
          <CardDescription>First rows detected in your file</CardDescription>
        </CardHeader>
        <CardContent>
          {rows.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-muted/30 p-10 text-center text-sm text-muted-foreground">
              Upload a file to preview its contents here.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Merchant</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.slice(0, 8).map((r, i) => (
                    <TableRow key={`${r.merchant}-${i}`}>
                      <TableCell className="whitespace-nowrap text-muted-foreground">
                        {r.date}
                      </TableCell>
                      <TableCell className="font-medium">{r.merchant}</TableCell>
                      <TableCell>{r.category}</TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatMoney(r.amount, true)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
