import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";
import { clsx } from "clsx";

type ToastKind = "success" | "error" | "info";

interface ToastMessage {
  id: number;
  kind: ToastKind;
  text: string;
}

interface ToastContextValue {
  notify: (text: string, kind?: ToastKind) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  const remove = useCallback((id: number) => {
    setMessages((current) => current.filter((message) => message.id !== id));
  }, []);

  const notify = useCallback((text: string, kind: ToastKind = "info") => {
    const id = Date.now();
    setMessages((current) => [...current, { id, kind, text }]);
    window.setTimeout(() => remove(id), 3600);
  }, [remove]);

  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3" aria-live="polite">
        {messages.map((message) => {
          const Icon = message.kind === "success" ? CheckCircle2 : message.kind === "error" ? XCircle : Info;
          return (
            <div
              key={message.id}
              className={clsx(
                "flex items-start gap-3 rounded-lg border bg-white p-4 text-sm shadow-soft",
                message.kind === "success" && "border-green-200",
                message.kind === "error" && "border-red-200",
                message.kind === "info" && "border-blue-200",
              )}
            >
              <Icon className={clsx("mt-0.5 h-5 w-5 shrink-0", message.kind === "success" && "text-accent", message.kind === "error" && "text-danger", message.kind === "info" && "text-primary")} />
              <p className="flex-1 text-slate-700">{message.text}</p>
              <button type="button" aria-label="Dismiss notification" onClick={() => remove(message.id)} className="rounded p-1 text-slate-500 hover:bg-slate-100">
                <X className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const value = useContext(ToastContext);
  if (!value) throw new Error("useToast must be used inside ToastProvider");
  return value;
}
