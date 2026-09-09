import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/common/app-shell";
import { UploadPanel } from "@/dashboard/upload-panel";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "Upload — AI Expense Analyzer" },
      {
        name: "description",
        content:
          "Import expenses from CSV or JSON with instant validation, row preview and upload status feedback.",
      },
      { property: "og:title", content: "Upload — AI Expense Analyzer" },
      {
        property: "og:description",
        content: "Drag and drop a CSV or JSON statement and preview the parsed rows.",
      },
    ],
  }),
  component: UploadPage,
});

function UploadPage() {
  return (
    <AppShell title="Upload" description="Import a CSV or JSON statement">
      <UploadPanel />
    </AppShell>
  );
}
