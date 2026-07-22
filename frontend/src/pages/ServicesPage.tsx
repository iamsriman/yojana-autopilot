import { useEffect, useMemo, useState } from "react";
import { Clock, ExternalLink, FileText, IndianRupee, Search } from "lucide-react";
import { getPortal, searchServices } from "../api/yojana";
import { getApiError } from "../api/client";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { SkeletonCard } from "../components/ui/Loader";
import { SearchBar } from "../components/ui/SearchBar";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useLocalStorage } from "../hooks/useLocalStorage";
import { serviceCategories } from "../data/constants";
import type { PortalResponse, ServiceSearchResult } from "../types/api";

export default function ServicesPage() {
  const initialQuery = new URLSearchParams(window.location.search).get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [category, setCategory] = useState("all");
  const [results, setResults] = useState<ServiceSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<ServiceSearchResult | null>(null);
  const [portal, setPortal] = useState<PortalResponse | null>(null);
  const [portalError, setPortalError] = useState("");
  const [history, setHistory] = useLocalStorage<string[]>("yojana:service-history", []);
  const debouncedQuery = useDebouncedValue(query);

  useEffect(() => {
    let active = true;
    const term = debouncedQuery.trim();
    if (!term && category === "all") {
      setResults([]);
      setError("");
      return;
    }
    setLoading(true);
    setError("");
    searchServices({
      query: term || undefined,
      category: category === "all" ? undefined : category,
      top_k: 20,
    })
      .then((data) => {
        if (!active) return;
        setResults(data);
        if (term) setHistory((current) => [term, ...current.filter((item) => item.toLowerCase() !== term.toLowerCase())].slice(0, 6));
      })
      .catch((apiError) => {
        if (active) setError(getApiError(apiError));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [debouncedQuery, category, setHistory]);

  useEffect(() => {
    let active = true;
    setPortal(null);
    setPortalError("");
    if (!selected?.portal) return;
    getPortal(selected.portal)
      .then((data) => {
        if (active) setPortal(data);
      })
      .catch((apiError) => {
        if (active) setPortalError(getApiError(apiError));
      });
    return () => {
      active = false;
    };
  }, [selected]);

  const heading = useMemo(() => {
    if (query.trim()) return `Results for "${query.trim()}"`;
    if (category !== "all") return `${category} services`;
    return "Search government services";
  }, [query, category]);

  return (
    <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-extrabold text-slate-950">Government Services</h1>
        <p className="mt-3 text-slate-600">Search service names, Telugu aliases, documents, categories, and common keywords.</p>
      </div>
      <div className="mt-6 grid gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-soft">
        <SearchBar value={query} onChange={setQuery} placeholder="Search services, certificates, documents..." label="Search services" />
        <div className="flex gap-2 overflow-x-auto pb-1">
          {serviceCategories.map((item) => (
            <button key={item} type="button" onClick={() => setCategory(item)} className={item === category ? "shrink-0 rounded-md bg-primary px-3 py-2 text-sm font-semibold capitalize text-white" : "shrink-0 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold capitalize text-slate-700 hover:bg-slate-50"}>
              {item}
            </button>
          ))}
        </div>
        {history.length ? (
          <div className="text-sm text-slate-600">
            <span className="font-semibold text-slate-900">Recent services: </span>
            {history.map((item) => <button key={item} type="button" onClick={() => setQuery(item)} className="mr-3 mt-2 font-semibold text-primary hover:underline">{item}</button>)}
          </div>
        ) : null}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_360px]">
        <div>
          <h2 className="mb-4 text-xl font-bold text-slate-950">{heading}</h2>
          {loading ? <div className="grid gap-4 md:grid-cols-2"><SkeletonCard /><SkeletonCard /><SkeletonCard /><SkeletonCard /></div> : null}
          {error ? <ErrorState message={error} onRetry={() => setQuery((current) => current.trim() || "income certificate")} /> : null}
          {!loading && !error && !results.length ? (
            <EmptyState title="No services found" message="Try a different service name, document, or category. Examples: Aadhaar, birth certificate, land records, pension." />
          ) : null}
          {!loading && !error && results.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {results.map((service) => (
                <Card key={service.id} className="flex flex-col">
                  <div className="flex-1">
                    <div className="mb-3 flex items-start justify-between gap-3">
                      <h3 className="font-bold text-slate-950">{service.name}</h3>
                      {service.category ? <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-bold uppercase text-primary">{service.category}</span> : null}
                    </div>
                    <p className="line-clamp-3 text-sm leading-6 text-slate-600">{service.description}</p>
                    <div className="mt-4 grid gap-2 text-sm text-slate-700">
                      {service.processing_time ? <span className="inline-flex items-center gap-2"><Clock className="h-4 w-4 text-slate-400" /> {service.processing_time}</span> : null}
                      <span className="inline-flex items-center gap-2"><IndianRupee className="h-4 w-4 text-slate-400" /> Fee details available in official service flow</span>
                      <span className="inline-flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> {service.documents.length} required documents</span>
                    </div>
                  </div>
                  <Button variant="secondary" className="mt-5 w-full" onClick={() => setSelected(service)}>Open Details</Button>
                </Card>
              ))}
            </div>
          ) : null}
        </div>
        <aside className="lg:sticky lg:top-24 lg:self-start">
          <Card>
            {!selected ? (
              <div className="py-8 text-center">
                <Search className="mx-auto h-9 w-9 text-primary" aria-hidden="true" />
                <h2 className="mt-3 font-bold text-slate-950">Select a service</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">Open details to see documents, offices, processing time, and official portal.</p>
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-bold text-slate-950">{selected.name}</h2>
                <p className="mt-3 text-sm leading-6 text-slate-600">{selected.description}</p>
                <DetailList title="Required documents" items={selected.documents} />
                <DetailList title="Office types" items={selected.offices} />
                {selected.processing_time ? <p className="mt-4 text-sm"><strong>Processing time:</strong> {selected.processing_time}</p> : null}
                {portal ? (
                  <div className="mt-5 rounded-md bg-slate-50 p-4">
                    <h3 className="font-bold text-slate-900">{portal.name}</h3>
                    {portal.owner ? <p className="mt-1 text-sm text-slate-600">{portal.owner}</p> : null}
                    {portal.helpline ? <p className="mt-2 text-sm"><strong>Helpline:</strong> {portal.helpline}</p> : null}
                    {portal.portal_url ? (
                      <a href={portal.portal_url} target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-semibold text-white">
                        Open official portal <ExternalLink className="h-4 w-4" />
                      </a>
                    ) : null}
                  </div>
                ) : selected.portal && !portalError ? <p className="mt-4 text-sm text-slate-500">Loading portal details...</p> : null}
                {portalError ? <p className="mt-4 text-sm text-danger">{portalError}</p> : null}
              </div>
            )}
          </Card>
        </aside>
      </div>
    </section>
  );
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="mt-5">
      <h3 className="font-bold text-slate-900">{title}</h3>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-slate-700">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
