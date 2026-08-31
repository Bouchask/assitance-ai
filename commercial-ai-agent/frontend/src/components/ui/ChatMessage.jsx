import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, ShieldCheck, Sparkles, X, Calendar, Table } from "lucide-react";

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

  const renderValue = (value) => {
    if (Array.isArray(value)) {
      return (
        <div className="flex flex-col gap-1.5 mt-1">
          {value.map((item, i) => (
            <div key={i} className="rounded bg-black/20 p-2 text-xs border border-white/5">
              {typeof item === 'object' && item !== null ? Object.entries(item).map(([k, v]) => (
                <div key={k} className="flex gap-2">
                  <span className="text-zinc-500">{k}:</span>
                  <span className="text-zinc-300">{String(v)}</span>
                </div>
              )) : String(item)}
            </div>
          ))}
        </div>
      );
    }
    if (typeof value === 'object' && value !== null) {
      return <span className="text-zinc-300">{JSON.stringify(value)}</span>;
    }
  };

  const renderEmailPreview = (args) => {
    let attachments = args.attachments;
    if (typeof attachments === 'string') {
      try { attachments = JSON.parse(attachments); } catch(e) { attachments = [attachments]; }
    }
    if (!Array.isArray(attachments)) attachments = [];

    return (
      <div className="mt-4 bg-[#1a1a1a] rounded-lg border border-white/10 overflow-hidden text-[13px] shadow-inner">
        {/* Email Header */}
        <div className="p-4 border-b border-white/5 bg-white/[0.02]">
          <div className="flex gap-4 items-center mb-2">
            <span className="text-zinc-500 font-medium text-xs uppercase tracking-wider w-16 shrink-0">À :</span>
            <span className="text-emerald-400 font-medium">{args.to}</span>
          </div>
          <div className="flex gap-4 items-center">
            <span className="text-zinc-500 font-medium text-xs uppercase tracking-wider w-16 shrink-0">Objet :</span>
            <span className="text-zinc-100 font-semibold">{args.subject}</span>
          </div>
        </div>

        {/* Email Body */}
        <div className="p-4 border-b border-white/5 text-zinc-300 whitespace-pre-wrap leading-relaxed">
          {args.body}
        </div>

        {/* Attachments & Preview */}
        {attachments.length > 0 && (
          <div className="p-4 bg-black/20">
            <h4 className="text-zinc-500 font-medium text-xs uppercase tracking-wider mb-3">Pièces jointes ({attachments.length})</h4>
            <div className="flex flex-col gap-4">
              {attachments.map((path, idx) => {
                const filename = path.split('/').pop().split('\\').pop();
                const url = `http://localhost:5001/api/documents/${filename}`;
                const isPdf = filename.toLowerCase().endsWith('.pdf');
                return (
                  <div key={idx} className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded px-3 py-2 text-zinc-300 w-fit">
                      <span className="grid place-items-center bg-emerald-500/20 text-emerald-400 rounded size-6 text-[10px] font-bold">
                        {isPdf ? 'PDF' : 'DOC'}
                      </span>
                      <span className="text-xs truncate max-w-[250px]">{filename}</span>
                    </div>
                    {/* Mini-window preview */}
                    <div className="w-full h-[400px] border border-white/10 rounded-lg overflow-hidden bg-white mt-1 relative">
                      <iframe src={url} className="w-full h-full border-0" title={`Aperçu ${filename}`} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCalendarPreview = (args) => {
    return (
      <div className="mt-4 bg-[#1a1a1a] rounded-lg border border-white/10 overflow-hidden text-[13px] shadow-inner">
        <div className="p-4 border-b border-white/5 bg-blue-500/10 flex items-center gap-3">
          <Calendar className="size-5 text-blue-400" />
          <span className="text-blue-100 font-semibold text-sm">Google Calendar Meeting</span>
        </div>
        <div className="p-4 flex flex-col gap-3">
          <div className="flex gap-4">
            <span className="text-zinc-500 font-medium w-24 shrink-0">Titre :</span>
            <span className="text-zinc-200 font-medium">{args.title}</span>
          </div>
          <div className="flex gap-4">
            <span className="text-zinc-500 font-medium w-24 shrink-0">Date / Heure :</span>
            <span className="text-emerald-400">{new Date(args.start_time).toLocaleString('fr-FR')}</span>
          </div>
          {args.attendees && args.attendees.length > 0 && (
            <div className="flex gap-4">
              <span className="text-zinc-500 font-medium w-24 shrink-0">Invités :</span>
              <span className="text-zinc-300">{args.attendees.join(', ')}</span>
            </div>
          )}
          {args.description && (
            <div className="flex gap-4">
              <span className="text-zinc-500 font-medium w-24 shrink-0">Description :</span>
              <span className="text-zinc-400 text-xs">{args.description}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderSheetsPreview = (args) => {
    return (
      <div className="mt-4 bg-[#1a1a1a] rounded-lg border border-white/10 overflow-hidden text-[13px] shadow-inner">
        <div className="p-4 border-b border-white/5 bg-green-500/10 flex items-center gap-3">
          <Table className="size-5 text-green-400" />
          <span className="text-green-100 font-semibold text-sm">Google Sheets Export</span>
        </div>
        <div className="p-4 flex flex-col gap-3">
          <div className="flex gap-4">
            <span className="text-zinc-500 font-medium w-24 shrink-0">ID Fichier :</span>
            <span className="text-zinc-200 font-mono text-xs">{args.spreadsheet_id || "Automatique (Nouveau ou Existant)"}</span>
          </div>
          <div className="flex gap-4">
            <span className="text-zinc-500 font-medium w-24 shrink-0">Données :</span>
            <div className="flex gap-2 flex-wrap">
              {args.values?.map((val, i) => (
                <span key={i} className="bg-white/5 border border-white/10 px-2 py-1 rounded text-zinc-300">
                  {String(val)}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <article className="flex gap-3 py-4 sm:gap-4 sm:py-5">
      <div className="mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-emerald-600 text-white shadow-sm">
        <Sparkles className="size-3.5" />
      </div>
      <div className="min-w-0 flex-1 pt-0.5">
        <div className="agent-markdown text-[15px] leading-7 text-zinc-100">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              a: ({node, ...props}) => {
                const isCalendar = props.href?.includes('calendar.google.com');
                const isSheets = props.href?.includes('docs.google.com/spreadsheets');
                
                return (
                  <a href={props.href} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 text-[13px] font-medium text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/50 transition-all my-2 shadow-sm">
                    {isCalendar && <Calendar className="size-3.5" />}
                    {isSheets && <Table className="size-3.5" />}
                    {isCalendar ? "Ouvrir dans Google Agenda" : isSheets ? "Ouvrir dans Google Sheets" : "Ouvrir le lien"}
                  </a>
                );
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.approval && (
          <section className="approval-card mt-4 rounded-xl bg-[#222] border border-amber-500/20 p-4 shadow-lg shadow-black/20">
            <div className="flex items-start gap-3">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-amber-400/10 text-amber-300"><ShieldCheck className="size-4" /></span>
              <div>
                <h2 className="text-sm font-semibold text-amber-200/90">Validation requise</h2>
                <p className="mt-0.5 text-xs leading-5 text-zinc-400">L’agent souhaite exécuter <span className="font-mono text-[11px] text-amber-300/80 bg-amber-500/10 px-1 py-0.5 rounded">{message.approval.tool}</span>.</p>
              </div>
            </div>
            
            {['db.create_quote', 'document.generate'].includes(message.approval.tool) && message.approval.arguments ? (
              <div className="mt-4 bg-[#1a1a1a] rounded-lg border border-white/10 overflow-hidden text-[13px] shadow-inner">
                {/* Header */}
                <div className="flex justify-between items-end p-4 border-b border-white/5 bg-white/[0.02]">
                  <div>
                    <h3 className="text-lg font-semibold text-zinc-100 uppercase tracking-widest">
                      {message.approval.arguments.document_type === 'invoice' ? 'Facture' : 'Devis'}
                    </h3>
                    <p className="text-zinc-400 mt-1">{message.approval.arguments.client_name || `Client #${message.approval.arguments.client_id || 'N/A'}`}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-zinc-500 text-xs uppercase tracking-wider mb-0.5">Montant TTC</p>
                    <p className="text-xl font-medium text-emerald-400">{(message.approval.arguments.total_ttc || 0).toFixed(2)} €</p>
                  </div>
                </div>

                {/* Items */}
                <div className="p-0">
                  <div className="grid grid-cols-12 gap-2 px-4 py-2 border-b border-white/5 bg-black/20 text-zinc-500 text-[10px] font-medium uppercase tracking-wider">
                    <div className="col-span-6">Description</div>
                    <div className="col-span-2 text-right">Qté</div>
                    <div className="col-span-2 text-right">Prix U.</div>
                    <div className="col-span-2 text-right">Total</div>
                  </div>
                  <div className="flex flex-col">
                    {message.approval.arguments.items?.map((item, idx) => (
                      <div key={idx} className="grid grid-cols-12 gap-2 px-4 py-3 border-b border-white/5 last:border-0 text-zinc-300">
                        <div className="col-span-6">
                          <div className="font-medium text-zinc-200">{item.code}</div>
                          {item.description && <div className="text-zinc-500 text-xs truncate mt-0.5">{item.description}</div>}
                        </div>
                        <div className="col-span-2 text-right">{item.quantity}</div>
                        <div className="col-span-2 text-right">{(item.price || item.unit_price || 0).toFixed(2)} €</div>
                        <div className="col-span-2 text-right font-medium">{(item.line_total || (item.quantity * (item.price || item.unit_price || 0))).toFixed(2)} €</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Totals summary */}
                <div className="bg-black/40 p-4 flex justify-end">
                  <div className="w-48 flex flex-col gap-1.5 text-xs">
                    <div className="flex justify-between text-zinc-400">
                      <span>Total HT</span>
                      <span>{(message.approval.arguments.total_ht || message.approval.arguments.original_subtotal || 0).toFixed(2)} €</span>
                    </div>
                    {message.approval.arguments.discount_amount > 0 && (
                      <div className="flex justify-between text-amber-400/80">
                        <span>Remise</span>
                        <span>-{(message.approval.arguments.discount_amount || 0).toFixed(2)} €</span>
                      </div>
                    )}
                    <div className="flex justify-between text-zinc-400">
                      <span>TVA</span>
                      <span>{(message.approval.arguments.tax || message.approval.arguments.total_tax || 0).toFixed(2)} €</span>
                    </div>
                    <div className="flex justify-between text-emerald-400 font-medium pt-1.5 border-t border-white/10 mt-1 text-[13px]">
                      <span>Total TTC</span>
                      <span>{(message.approval.arguments.total_ttc || 0).toFixed(2)} €</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : message.approval.tool === 'email.send' && message.approval.arguments ? (
              renderEmailPreview(message.approval.arguments)
            ) : message.approval.tool === 'google.calendar.create_meeting' && message.approval.arguments ? (
              renderCalendarPreview(message.approval.arguments)
            ) : message.approval.tool === 'google.sheets.append_row' && message.approval.arguments ? (
              renderSheetsPreview(message.approval.arguments)
            ) : (
              <div className="mt-4 rounded-lg bg-black/40 border border-white/5 overflow-hidden">
                <div className="px-3 py-2 border-b border-white/5 bg-white/5 text-[10px] font-medium text-zinc-400 uppercase tracking-wider flex justify-between items-center">
                  <span>Données de la requête</span>
                </div>
                <div className="p-3 grid gap-1 text-[13px]">
                  {message.approval.arguments && Object.entries(message.approval.arguments).map(([key, value]) => (
                    <div key={key} className="flex flex-col sm:flex-row sm:items-start gap-1 py-1.5 border-b border-white/5 last:border-0">
                      <div className="text-zinc-500 font-medium sm:w-1/3 shrink-0">{key}</div>
                      <div className="text-zinc-300 break-words flex-1">{renderValue(value)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
              <button onClick={() => onApprove(message.approval, true)} className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-[13px] font-medium text-white hover:bg-emerald-500 transition-colors">
                <Check className="size-3.5" /> Approuver
              </button>
              <button onClick={() => onApprove(message.approval, false)} className="inline-flex items-center gap-1.5 rounded-lg bg-zinc-800 border border-white/10 px-3 py-1.5 text-[13px] font-medium text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors">
                <X className="size-3.5" /> Refuser
              </button>
            </div>
          </section>
        )}
      </div>
    </article>
  );
}
