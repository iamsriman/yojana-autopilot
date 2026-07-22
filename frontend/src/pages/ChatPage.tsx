import { FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, Clipboard, Send, Trash2, User } from "lucide-react";
import { askAssistant } from "../api/yojana";
import { getApiError } from "../api/client";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { TypingIndicator } from "../components/ui/Loader";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { useToast } from "../components/ui/Toast";
import { districts } from "../data/constants";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
}

const suggestedQuestions = [
  "How do I apply for an income certificate in Guntur?",
  "What documents are needed for Aadhaar address update?",
  "Where can I apply for PM Kisan in Andhra Pradesh?",
  "How do I find a nearby MeeSeva centre?",
];

export default function ChatPage() {
  const [messages, setMessages] = useLocalStorage<ChatMessage[]>("yojana:chat-history", []);
  const [question, setQuestion] = useState("");
  const [district, setDistrict] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);
  const { notify } = useToast();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text = question) {
    const trimmed = text.trim();
    if (trimmed.length < 3 || loading) return;
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: trimmed };
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setLoading(true);
    try {
      const response = await askAssistant(trimmed, district || undefined);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          confidence: response.confidence,
        },
      ]);
    } catch (error) {
      notify(getApiError(error), "error");
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void send();
  }

  async function copyResponse(content: string) {
    await navigator.clipboard.writeText(content);
    notify("Response copied.", "success");
  }

  return (
    <section className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
      <aside className="space-y-4">
        <Card>
          <label htmlFor="chat-district" className="text-sm font-semibold text-slate-800">District</label>
          <select id="chat-district" value={district} onChange={(event) => setDistrict(event.target.value)} className="mt-2 min-h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
            <option value="">Any district</option>
            {districts.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-slate-950">Suggested questions</h2>
          </div>
          <div className="mt-4 grid gap-2">
            {suggestedQuestions.map((item) => (
              <button key={item} type="button" onClick={() => void send(item)} className="rounded-md border border-slate-200 bg-white p-3 text-left text-sm leading-5 text-slate-700 hover:border-blue-200 hover:bg-blue-50">
                {item}
              </button>
            ))}
          </div>
        </Card>
        <Button variant="secondary" icon={<Trash2 className="h-4 w-4" />} onClick={() => setMessages([])} className="w-full">
          Clear conversation
        </Button>
      </aside>
      <div className="flex min-h-[72vh] flex-col rounded-lg border border-slate-200 bg-white shadow-soft">
        <div className="border-b border-slate-200 p-4">
          <h1 className="text-xl font-extrabold text-slate-950">AI Assistant</h1>
          <p className="mt-1 text-sm text-slate-600">Ask about Andhra Pradesh services, documents, eligibility, or offices.</p>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {!messages.length ? (
            <div className="flex h-full min-h-[360px] flex-col items-center justify-center text-center">
              <Bot className="h-12 w-12 text-primary" aria-hidden="true" />
              <h2 className="mt-4 text-lg font-bold text-slate-950">How can I help today?</h2>
              <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">Try a question about a certificate, welfare scheme, document list, or nearby office.</p>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((message) => (
                <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
                  <div className={message.role === "user" ? "max-w-[86%] rounded-lg bg-primary p-4 text-white" : "max-w-[92%] rounded-lg bg-slate-50 p-4 text-slate-800"}>
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <span className="inline-flex items-center gap-2 text-xs font-bold uppercase">
                        {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        {message.role === "user" ? "You" : "Assistant"}
                      </span>
                      {message.role === "assistant" ? (
                        <button type="button" onClick={() => void copyResponse(message.content)} className="rounded p-1 text-slate-500 hover:bg-white" aria-label="Copy assistant response">
                          <Clipboard className="h-4 w-4" />
                        </button>
                      ) : null}
                    </div>
                    <div className="prose prose-sm max-w-none prose-pre:overflow-x-auto prose-pre:rounded-md prose-pre:bg-slate-900 prose-pre:p-3 prose-pre:text-slate-50">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                    </div>
                    {message.confidence !== undefined ? <p className="mt-2 text-xs text-slate-500">Confidence: {Math.round(message.confidence * 100)}%</p> : null}
                  </div>
                </div>
              ))}
              {loading ? (
                <div className="flex justify-start">
                  <div className="rounded-lg bg-slate-50 p-4"><TypingIndicator /></div>
                </div>
              ) : null}
              <div ref={endRef} />
            </div>
          )}
        </div>
        <form onSubmit={submit} className="border-t border-slate-200 p-4">
          <div className="flex gap-3">
            <label htmlFor="chat-question" className="sr-only">Ask a question</label>
            <textarea id="chat-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Type your question..." rows={1} className="min-h-12 flex-1 resize-none rounded-md border border-slate-200 px-4 py-3 text-sm" />
            <Button type="submit" disabled={loading || question.trim().length < 3} icon={<Send className="h-4 w-4" />}>Send</Button>
          </div>
        </form>
      </div>
    </section>
  );
}
