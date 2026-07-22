import type { ReactNode } from "react";
import { SearchX } from "lucide-react";
import { Card } from "./Card";

interface EmptyStateProps {
  title: string;
  message: string;
  action?: ReactNode;
}

export function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <Card className="flex flex-col items-center justify-center py-10 text-center">
      <div className="mb-4 rounded-full bg-slate-100 p-4 text-slate-500">
        <SearchX className="h-8 w-8" aria-hidden="true" />
      </div>
      <h2 className="text-lg font-bold text-slate-900">{title}</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">{message}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </Card>
  );
}
