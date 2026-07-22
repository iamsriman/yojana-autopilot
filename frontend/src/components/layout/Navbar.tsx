import { useState } from "react";
import { Bot, Building2, CheckCircle2, Home, Info, Menu, MessageSquare, Search, X } from "lucide-react";
import { clsx } from "clsx";
import { routes, useRoute } from "../../router";

const icons = {
  Home,
  "AI Assistant": MessageSquare,
  Eligibility: CheckCircle2,
  Services: Search,
  Offices: Building2,
  About: Info,
};

export function Navbar() {
  const [open, setOpen] = useState(false);
  const { path, navigate } = useRoute();

  const links = routes.filter((route) => route.showInNav);

  function go(nextPath: string) {
    navigate(nextPath);
    setOpen(false);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8" aria-label="Main navigation">
        <button type="button" onClick={() => go("/")} className="flex items-center gap-3 rounded-md text-left">
          <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-white">
            <Bot className="h-5 w-5" aria-hidden="true" />
          </span>
          <span>
            <span className="block text-base font-extrabold text-slate-950">Yojana Autopilot</span>
            <span className="block text-xs font-medium text-slate-500">Andhra Pradesh Service Assistant</span>
          </span>
        </button>
        <div className="hidden items-center gap-1 lg:flex">
          {links.map((route) => {
            const Icon = icons[route.label as keyof typeof icons];
            return (
              <button
                key={route.path}
                type="button"
                onClick={() => go(route.path)}
                className={clsx(
                  "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition",
                  path === route.path ? "bg-blue-50 text-primary" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                )}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {route.label}
              </button>
            );
          })}
        </div>
        <button type="button" className="rounded-md p-2 text-slate-700 hover:bg-slate-100 lg:hidden" aria-label="Toggle navigation" onClick={() => setOpen((value) => !value)}>
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>
      {open ? (
        <div className="border-t border-slate-200 bg-white px-4 py-3 lg:hidden">
          <div className="grid gap-2">
            {links.map((route) => {
              const Icon = icons[route.label as keyof typeof icons];
              return (
                <button key={route.path} type="button" onClick={() => go(route.path)} className="flex items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-semibold text-slate-700 hover:bg-slate-100">
                  <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
                  {route.label}
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
    </header>
  );
}
