import { useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { clsx } from "clsx";

interface AccordionProps {
  title: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function Accordion({ title, children, defaultOpen = false }: AccordionProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <button type="button" onClick={() => setOpen((value) => !value)} className="flex w-full items-center justify-between gap-4 p-4 text-left">
        <span className="font-semibold text-slate-900">{title}</span>
        <ChevronDown className={clsx("h-5 w-5 shrink-0 text-slate-500 transition", open && "rotate-180")} />
      </button>
      {open ? <div className="border-t border-slate-100 p-4 text-sm leading-6 text-slate-700">{children}</div> : null}
    </div>
  );
}
