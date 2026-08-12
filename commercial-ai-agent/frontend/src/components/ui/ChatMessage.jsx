import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, ShieldCheck, Sparkles, X } from "lucide-react";

export function ChatMessage({ message, onApprove }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <article className="flex justify-end py-3 sm:py-4">
        <div className="max-w-[88%] rounded-[1.35rem] bg-[#303030] px-4 py-2.5 text-[15px] leading-6 text-zinc-100 sm:max-w-[78%]">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
      </article>
    );
  }

  return (
    <article className="flex gap-3 py-4 sm:gap-4 sm:py-5">
      <div className="mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-emerald-600 text-white shadow-sm">
        <Sparkles className="size-3.5" />
      </div>
      <div className="min-w-0 flex-1 pt-0.5">
        <div className="agent-markdown text-[15px] leading-7 text-zinc-100">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {message.approval && (
          <section className="approval-card">
            <div className="flex items-start gap-3">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-amber-400/10 text-amber-300"><ShieldCheck className="size-4" /></span>
              <div>
                <h2 className="text-sm font-semibold text-zinc-100">Validation requise</h2>
                <p className="mt-0.5 text-xs leading-5 text-zinc-400">L’agent souhaite exécuter <span className="font-medium text-zinc-300">{message.approval.tool}</span>.</p>
              </div>
            </div>
            <pre className="approval-payload">{JSON.stringify(message.approval.arguments, null, 2)}</pre>
            <div className="mt-3 flex flex-wrap gap-2">
              <button onClick={() => onApprove(message.approval, true)} className="approval-primary"><Check className="size-4" /> Approuver</button>
              <button onClick={() => onApprove(message.approval, false)} className="approval-secondary"><X className="size-4" /> Refuser</button>
            </div>
          </section>
        )}
      </div>
    </article>
  );
}
