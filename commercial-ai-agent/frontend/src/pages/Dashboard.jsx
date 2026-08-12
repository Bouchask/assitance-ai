import React, { useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  Bot,
  ChevronDown,
  CircleHelp,
  Menu,
  MessageSquarePlus,
  Paperclip,
  Plus,
  Search,
  Settings,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";
import { ChatMessage } from "../components/ui/ChatMessage";

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

const WELCOME_MESSAGE = {
  role: "agent",
  content:
    "Bonjour ! Je peux préparer un devis, rechercher vos prestations et envoyer un email après votre validation.",
};

const SUGGESTIONS = [
  "Crée un devis pour Atlas E-Commerce Group avec un site e-commerce et une optimisation SEO.",
  "Prépare un devis pour un site vitrine avec 6 mois de maintenance.",
  "Quels services sont disponibles dans le catalogue ?",
];

const RECENT_CHATS = [
  "Devis Atlas E-Commerce",
  "Proposition de maintenance",
  "Catalogue des services",
];

function Sidebar({ open, onClose, onNewChat, user, onLogout }) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-[272px] flex-col border-r border-white/[0.07] bg-[#171717] p-2 transition-transform duration-200 md:static md:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="flex items-center justify-between px-2 py-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
          <span className="grid size-7 place-items-center rounded-lg bg-zinc-100 text-zinc-900">
            <Sparkles className="size-4" />
          </span>
          Commercial AI
        </div>
        <button onClick={onClose} className="icon-button md:hidden" aria-label="Fermer le menu">
          <X className="size-4" />
        </button>
      </div>

      <button onClick={onNewChat} className="new-chat-button">
        <MessageSquarePlus className="size-[18px]" />
        Nouvelle discussion
      </button>

      <div className="mt-5 flex-1 overflow-y-auto px-1">
        <div className="sidebar-label">Récentes</div>
        <div className="mt-1 space-y-0.5">
          {RECENT_CHATS.map((chat, index) => (
            <button key={chat} className={`sidebar-chat ${index === 0 ? "sidebar-chat-active" : ""}`}>
              <Bot className="size-4 shrink-0" />
              <span className="truncate">{chat}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-1 border-t border-white/[0.07] pt-2">
        <button className="sidebar-chat">
          <CircleHelp className="size-4" />
          Aide
        </button>
        <button className="sidebar-chat">
          <Settings className="size-4" />
          Paramètres
        </button>
        <button onClick={onLogout} className="mt-1 flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left text-sm text-zinc-200 hover:bg-red-500/10 hover:text-red-400 transition-colors">
          <span className="grid size-7 place-items-center rounded-full bg-emerald-700 text-xs font-semibold text-white">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </span>
          <span className="min-w-0 flex-1 truncate">{user?.email || 'Utilisateur'}</span>
          <span className="text-xs opacity-60">Déconnexion</span>
        </button>
      </div>
    </aside>
  );
}

export default function Dashboard({ user, onLogout }) {
  const [prompt, setPrompt] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [threadId, setThreadId] = useState(() => crypto.randomUUID());
  
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, isTyping]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [prompt]);

  const appendResult = (data, fallbackMessages) => {
    if (data.status === "completed") {
      setMessages([...fallbackMessages, { role: "agent", content: data.response }]);
      return;
    }
    if (data.status === "waiting_approval") {
      setMessages([
        ...fallbackMessages,
        {
          role: "agent",
          content: "Votre validation est requise avant de poursuivre.",
          approval: {
            execution_id: data.execution_id,
            step_id: data.step,
            tool: data.tool,
            arguments: data.arguments,
          },
        },
      ]);
      return;
    }
    setMessages([
      ...fallbackMessages,
      { role: "agent", content: `Je n’ai pas pu terminer cette action.\n\n> ${data.error || data.message || "Erreur inconnue"}` },
    ]);
  };

  const requestApi = async (path, payload) => {
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
      },
      body: JSON.stringify(payload),
    });
    
    if (response.status === 401) {
      onLogout();
      throw new Error("Session expirée. Veuillez vous reconnecter.");
    }
    
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Erreur serveur (${response.status})`);
    return data;
  };

  const handleApprove = async (approval, approved) => {
    setMessages((current) =>
      current.map((message) =>
        message.approval?.execution_id === approval.execution_id
          ? {
              ...message,
              approval: null,
              content: `${message.content}\n\n> Action ${approved ? "approuvée" : "refusée"}.`,
            }
          : message,
      ),
    );
    setIsTyping(true);
    try {
      const data = await requestApi("/api/approve", { ...approval, approved, thread_id: threadId });
      setMessages((current) => {
        if (data.status === "completed") return [...current, { role: "agent", content: data.response }];
        if (data.status === "waiting_approval") {
          return [...current, {
            role: "agent",
            content: "Une autre validation est requise pour continuer.",
            approval: { execution_id: data.execution_id, step_id: data.step, tool: data.tool, arguments: data.arguments },
          }];
        }
        return [...current, { role: "agent", content: `> ${data.error || data.message || "Action non terminée"}` }];
      });
    } catch (error) {
      setMessages((current) => [...current, { role: "agent", content: `> Erreur de connexion : ${error.message}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = async (suggestion) => {
    const text = (suggestion ?? prompt).trim();
    if (!text || isTyping) return;
    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setPrompt("");
    setIsTyping(true);
    try {
      appendResult(await requestApi("/api/chat", { prompt: text, thread_id: threadId }), nextMessages);
    } catch (error) {
      setMessages([...nextMessages, { role: "agent", content: `> Erreur de connexion à l’API : ${error.message}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  const startNewChat = () => {
    setMessages([WELCOME_MESSAGE]);
    setPrompt("");
    setThreadId(crypto.randomUUID());
    setSidebarOpen(false);
    textareaRef.current?.focus();
  };

  return (
    <main className="flex h-[100dvh] overflow-hidden bg-[#212121] text-zinc-100">
      {isSidebarOpen && <button className="fixed inset-0 z-30 bg-black/55 md:hidden" onClick={() => setSidebarOpen(false)} aria-label="Fermer le menu" />}
      <Sidebar open={isSidebarOpen} onClose={() => setSidebarOpen(false)} onNewChat={startNewChat} user={user} onLogout={onLogout} />

      <section className="relative flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between px-3 md:px-5">
          <div className="flex items-center gap-2">
            <button onClick={() => setSidebarOpen(true)} className="icon-button md:hidden" aria-label="Ouvrir le menu">
              <Menu className="size-5" />
            </button>
            <button className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-medium text-zinc-100 hover:bg-white/[0.07]">
              Commercial AI <ChevronDown className="size-4 text-zinc-500" />
            </button>
          </div>
          <div className="flex items-center gap-1">
            <button className="icon-button hidden sm:grid" aria-label="Rechercher"><Search className="size-[18px]" /></button>
            <button className="icon-button hidden sm:grid" aria-label="Compte"><UserRound className="size-[18px]" /></button>
            <button onClick={startNewChat} className="icon-button md:hidden" aria-label="Nouvelle discussion"><Plus className="size-5" /></button>
          </div>
        </header>

        <div ref={scrollRef} className="chat-scroll flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-3xl px-4 pb-44 pt-5 sm:px-6 sm:pt-8">
            {messages.map((message, index) => (
              <ChatMessage key={`${message.role}-${index}`} message={message} onApprove={handleApprove} />
            ))}

            {messages.length === 1 && !isTyping && (
              <div className="mt-7 grid gap-2 sm:grid-cols-3">
                {SUGGESTIONS.map((suggestion) => (
                  <button key={suggestion} onClick={() => handleSend(suggestion)} className="suggestion-card">
                    <span>{suggestion}</span>
                    <ArrowUp className="size-4 shrink-0" />
                  </button>
                ))}
              </div>
            )}

            {isTyping && (
              <div className="flex items-center gap-3 py-5 text-sm text-zinc-400">
                <span className="grid size-7 place-items-center rounded-full bg-emerald-600 text-white"><Sparkles className="size-3.5" /></span>
                <span className="thinking-dots"><i /><i /><i /></span>
              </div>
            )}
          </div>
        </div>

        <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent px-3 pb-3 pt-12 sm:px-6 sm:pb-5">
          <div className="pointer-events-auto mx-auto max-w-3xl">
            <div className="composer-shell">
              <button className="icon-button mb-1 shrink-0" aria-label="Joindre un fichier" title="Les pièces jointes seront bientôt disponibles">
                <Paperclip className="size-[19px]" />
              </button>
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Message Commercial AI"
                rows="1"
                className="min-h-11 max-h-[200px] flex-1 resize-none bg-transparent py-3 text-[15px] leading-6 text-zinc-100 outline-none placeholder:text-zinc-500"
              />
              <button onClick={() => handleSend()} disabled={!prompt.trim() || isTyping} className="send-button" aria-label="Envoyer le message">
                <ArrowUp className="size-[19px] stroke-[2.5]" />
              </button>
            </div>
            <p className="mt-2 text-center text-[11px] text-zinc-500">Commercial AI peut faire des erreurs. Vérifiez les devis avant envoi.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
