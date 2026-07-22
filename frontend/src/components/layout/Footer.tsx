import { ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-8 text-sm text-slate-600 sm:px-6 md:grid-cols-[1fr_auto] lg:px-8">
        <div>
          <p className="font-semibold text-slate-900">Yojana Autopilot</p>
          <p className="mt-1 max-w-2xl leading-6">A citizen-first assistant for Andhra Pradesh government services, eligibility, offices, and official portals.</p>
        </div>
        <a className="inline-flex items-center gap-2 font-semibold text-primary" href="https://ap.gov.in" target="_blank" rel="noreferrer">
          Andhra Pradesh Portal
          <ExternalLink className="h-4 w-4" aria-hidden="true" />
        </a>
      </div>
    </footer>
  );
}
