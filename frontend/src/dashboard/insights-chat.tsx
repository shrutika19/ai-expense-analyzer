import { Send, Sparkle } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { answerQuestion, SUGGESTED_QUESTIONS } from "@/dashboard/insights";
import type { Expense, InsightMessage } from "@/types";

export function InsightsChat({ expenses }: { expenses: Expense[] }) {
  const [messages, setMessages] = useState<InsightMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Ask me anything about your spending. I'll summarise trends, flag outliers and suggest where to cut. Answers here are generated from the demo dataset.",
    },
  ]);
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, thinking]);

  function ask(question: string) {
    const q = question.trim();
    if (!q || thinking) return;
    setMessages((prev) => [...prev, { id: `u-${Date.now()}`, role: "user", content: q }]);
    setDraft("");
    setThinking(true);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { id: `a-${Date.now()}`, role: "assistant", content: answerQuestion(q, expenses) },
      ]);
      setThinking(false);
    }, 900);
  }

  return (
    <Card className="flex h-[640px] flex-col overflow-hidden">
      <CardContent className="flex min-h-0 flex-1 flex-col gap-4 p-4 md:p-5">
        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
          {messages.map((m) =>
            m.role === "user" ? (
              <div key={m.id} className="flex justify-end">
                <p className="max-w-[80%] rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground">
                  {m.content}
                </p>
              </div>
            ) : (
              <div key={m.id} className="flex gap-3">
                <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-accent/20">
                  <Sparkle className="size-3.5 text-accent-foreground" aria-hidden />
                </span>
                <p className="max-w-[85%] text-sm leading-relaxed text-foreground">{m.content}</p>
              </div>
            ),
          )}
          {thinking ? (
            <div className="flex gap-3">
              <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-accent/20">
                <Sparkle className="size-3.5 text-accent-foreground" aria-hidden />
              </span>
              <span className="animate-pulse text-sm text-muted-foreground">Analyzing…</span>
            </div>
          ) : null}
          <div ref={endRef} />
        </div>

        <div className="flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => ask(q)}
              disabled={thinking}
              className="rounded-full border border-border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask(draft);
          }}
          className="flex items-end gap-2"
        >
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                ask(draft);
              }
            }}
            placeholder="Why did my expenses increase this month?"
            rows={2}
            className="min-h-[52px] resize-none"
            aria-label="Ask a question about your spending"
          />
          <Button type="submit" size="icon" disabled={thinking || !draft.trim()} aria-label="Send">
            <Send className="size-4" aria-hidden />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
