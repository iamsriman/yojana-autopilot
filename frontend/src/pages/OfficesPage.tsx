import { useEffect, useMemo, useState } from "react";
import { MapPin, Phone, Star } from "lucide-react";
import { getOffices } from "../api/yojana";
import { getApiError } from "../api/client";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { SkeletonCard } from "../components/ui/Loader";
import { districts } from "../data/constants";
import type { Office, OfficesResponse } from "../types/api";

export default function OfficesPage() {
  const [district, setDistrict] = useState("Visakhapatnam");
  const [officeType, setOfficeType] = useState("all");
  const [data, setData] = useState<OfficesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    getOffices(district, officeType === "all" ? undefined : officeType)
      .then((response) => {
        if (active) setData(response);
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
  }, [district, officeType]);

  const officeTypes = useMemo(() => ["all", ...(data?.available_office_types ?? [])], [data]);

  return (
    <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-extrabold text-slate-950">Government Offices</h1>
        <p className="mt-3 text-slate-600">Find offices by district, working hours, contact details, and map location.</p>
      </div>
      <div className="mt-6 grid gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-soft md:grid-cols-2">
        <label className="grid gap-2 text-sm font-semibold text-slate-800">District
          <select value={district} onChange={(event) => { setDistrict(event.target.value); setOfficeType("all"); }} className="min-h-11 rounded-md border border-slate-200 px-3">
            {districts.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
        <label className="grid gap-2 text-sm font-semibold text-slate-800">Office type
          <select value={officeType} onChange={(event) => setOfficeType(event.target.value)} className="min-h-11 rounded-md border border-slate-200 px-3">
            {officeTypes.map((item) => <option key={item} value={item}>{item === "all" ? "All office types" : item}</option>)}
          </select>
        </label>
      </div>

      <div className="mt-8">
        {loading ? <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div> : null}
        {error ? <ErrorState message={error} onRetry={() => setDistrict((current) => current)} /> : null}
        {!loading && !error && !data?.offices.length ? <EmptyState title="No offices found" message="Try another district or choose all office types." /> : null}
        {!loading && !error && data?.offices.length ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.offices.map((office) => <OfficeCard key={`${office.name}-${office.address}`} office={office} />)}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function OfficeCard({ office }: { office: Office }) {
  const hours = office.hours ?? office.office_hours;
  const mapsUrl = office.latitude && office.longitude
    ? `https://www.google.com/maps/search/?api=1&query=${office.latitude},${office.longitude}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${office.name} ${office.address ?? ""}`)}`;

  return (
    <Card className="flex flex-col">
      <div className="flex-1">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-bold text-slate-950">{office.name}</h2>
          <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-bold uppercase text-primary">{office.office_type}</span>
        </div>
        {office.address ? <p className="mt-3 flex gap-2 text-sm leading-6 text-slate-600"><MapPin className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" /> {office.address}</p> : null}
        {hours ? <p className="mt-3 text-sm text-slate-700"><strong>Working hours:</strong> {hours}</p> : null}
        {office.phone ? <p className="mt-3 flex items-center gap-2 text-sm text-slate-700"><Phone className="h-4 w-4 text-slate-400" /> {office.phone}</p> : null}
        {office.rating ? <p className="mt-3 flex items-center gap-2 text-sm text-slate-700"><Star className="h-4 w-4 fill-amber-400 text-amber-400" /> {office.rating.toFixed(1)}</p> : null}
        {office.notes ? <p className="mt-3 text-sm leading-6 text-slate-600">{office.notes}</p> : null}
      </div>
      <a href={mapsUrl} target="_blank" rel="noreferrer" className="mt-5">
        <Button variant="secondary" className="w-full" icon={<MapPin className="h-4 w-4" />}>Google Maps</Button>
      </a>
    </Card>
  );
}
