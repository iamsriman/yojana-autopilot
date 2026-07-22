import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Bot, Building2, CheckCircle2, ExternalLink, Landmark, Search } from "lucide-react";
import { Card } from "../components/ui/Card";
import { SearchBar } from "../components/ui/SearchBar";
import { SkeletonCard } from "../components/ui/Loader";
import { EmptyState } from "../components/ui/EmptyState";
import { quickServices } from "../data/constants";
import { searchServices } from "../api/yojana";
import { getApiError } from "../api/client";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useLocalStorage } from "../hooks/useLocalStorage";
import type { ServiceSearchResult } from "../types/api";
import { useRoute } from "../router";

const features = [
  { title: "AI Assistance", text: "Ask service questions in simple language and get grounded answers.", icon: Bot, href: "/assistant" },
  { title: "Eligibility Check", text: "Check welfare scheme eligibility with a citizen-friendly form.", icon: CheckCircle2, href: "/eligibility" },
  { title: "Nearby Offices", text: "Find MeeSeva, RTO, collectorate, and other offices by district.", icon: Building2, href: "/offices" },
  { title: "Official Portals", text: "Open official portals connected to service search results.", icon: ExternalLink, href: "/services" },
];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ServiceSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recentSearches, setRecentSearches] = useLocalStorage<string[]>("yojana:recent-searches", []);
  const debouncedQuery = useDebouncedValue(query);
  const { navigate } = useRoute();

  useEffect(() => {
    let active = true;
    const term = debouncedQuery.trim();
    if (!term) {
      setResults([]);
      setError("");
      return;
    }
    setLoading(true);
    searchServices({ query: term, top_k: 4 })
      .then((data) => {
        if (active) setResults(data);
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
  }, [debouncedQuery]);

  const popularServices = useMemo(() => results.length ? results : [], [results]);

  function submitSearch(term = query) {
    const trimmed = term.trim();
    if (!trimmed) return;
    setRecentSearches((current) => [trimmed, ...current.filter((item) => item.toLowerCase() !== trimmed.toLowerCase())].slice(0, 6));
    navigate(`/services?q=${encodeURIComponent(trimmed)}`);
  }

  return (
    <div>
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:px-8 lg:py-16">
          <div className="flex flex-col justify-center">
            <p className="mb-4 inline-flex w-fit items-center gap-2 rounded-md bg-blue-50 px-3 py-1 text-sm font-semibold text-primary">
              <Landmark className="h-4 w-4" aria-hidden="true" />
              Andhra Pradesh citizen services
            </p>
            <h1 className="max-w-3xl text-4xl font-extrabold tracking-normal text-slate-950 sm:text-5xl">Find Government Services in Minutes</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">Search certificates, welfare schemes, nearby offices, and official portals with a simple assistant built for first-time users.</p>
            <div className="mt-8">
              <SearchBar value={query} onChange={setQuery} onSubmit={() => submitSearch()} label="Search government services" placeholder="Search for income certificate, pension, PM Kisan..." />
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {quickServices.map((service) => (
                <button key={service} type="button" onClick={() => { setQuery(service); submitSearch(service); }} className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-primary">
                  {service}
                </button>
              ))}
            </div>
            {recentSearches.length ? (
              <div className="mt-5 text-sm text-slate-600">
                <span className="font-semibold text-slate-800">Recent searches: </span>
                {recentSearches.map((item) => (
                  <button key={item} type="button" onClick={() => submitSearch(item)} className="mr-3 mt-2 font-semibold text-primary hover:underline">{item}</button>
                ))}
              </div>
            ) : null}
          </div>
          <div className="grid gap-4">
            <Card className="bg-slate-50">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-bold text-slate-950">Popular services</h2>
                <Search className="h-5 w-5 text-primary" aria-hidden="true" />
              </div>
              {loading ? <div className="grid gap-3"><SkeletonCard /><SkeletonCard /></div> : null}
              {!loading && error ? <p className="text-sm text-danger">{error}</p> : null}
              {!loading && !error && !popularServices.length ? (
                <div className="grid gap-3">
                  {quickServices.slice(0, 4).map((service) => (
                    <button key={service} type="button" onClick={() => submitSearch(service)} className="flex items-center justify-between rounded-md border border-slate-200 bg-white p-4 text-left font-semibold text-slate-800 hover:border-blue-200 hover:text-primary">
                      {service}
                      <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </button>
                  ))}
                </div>
              ) : null}
              {!loading && popularServices.length ? (
                <div className="grid gap-3">
                  {popularServices.map((service) => (
                    <button key={service.id} type="button" onClick={() => navigate(`/services?q=${encodeURIComponent(service.name)}`)} className="rounded-md border border-slate-200 bg-white p-4 text-left hover:border-blue-200">
                      <span className="block font-semibold text-slate-900">{service.name}</span>
                      <span className="mt-1 line-clamp-2 block text-sm text-slate-600">{service.description}</span>
                    </button>
                  ))}
                </div>
              ) : null}
            </Card>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <a key={feature.title} href={feature.href} className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft transition hover:-translate-y-0.5 hover:border-blue-200">
                <span className="mb-4 flex h-11 w-11 items-center justify-center rounded-md bg-blue-50 text-primary">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <h2 className="font-bold text-slate-950">{feature.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{feature.text}</p>
              </a>
            );
          })}
        </div>
      </section>
    </div>
  );
}
