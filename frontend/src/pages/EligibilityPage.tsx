import { FormEvent, useState } from "react";
import { ExternalLink } from "lucide-react";
import { checkEligibility } from "../api/yojana";
import { getApiError } from "../api/client";
import { Accordion } from "../components/ui/Accordion";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ErrorState } from "../components/ui/ErrorState";
import { SkeletonCard } from "../components/ui/Loader";
import { districts } from "../data/constants";
import type { EligibilityProfile, EligibilityResponse, SchemeDecision } from "../types/api";

const initialProfile: EligibilityProfile = {
  district: "Visakhapatnam",
  location: "rural",
  income: 9000,
  has_rice_card: true,
  has_ration_card: true,
  farmer: false,
  disabled: false,
  widow: false,
  student: false,
  four_wheeler: false,
  land: 0,
  electricity_units: 120,
};

function decisionTitle(decision: SchemeDecision) {
  const labels = {
    eligible: "Eligible",
    need_more_information: "Need More Information",
    not_eligible: "Not Eligible",
  };
  return `${decision.scheme_name} - ${labels[decision.status]}`;
}

export default function EligibilityPage() {
  const [profile, setProfile] = useState<EligibilityProfile>(initialProfile);
  const [result, setResult] = useState<EligibilityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function update<K extends keyof EligibilityProfile>(key: K, value: EligibilityProfile[K]) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setResult(await checkEligibility(profile));
    } catch (apiError) {
      setError(getApiError(apiError));
    } finally {
      setLoading(false);
    }
  }

  const groups = result ? [
    { key: "eligible", title: "Eligible", items: result.eligible, tone: "border-green-200 bg-green-50" },
    { key: "need_more_information", title: "Need More Information", items: result.need_more_information, tone: "border-blue-200 bg-blue-50" },
    { key: "not_eligible", title: "Not Eligible", items: result.not_eligible, tone: "border-red-200 bg-red-50" },
  ] : [];

  return (
    <section className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[360px_1fr] lg:px-8">
      <Card>
        <h1 className="text-2xl font-extrabold text-slate-950">Eligibility Checker</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">Enter citizen details to check matching welfare schemes.</p>
        <form onSubmit={submit} className="mt-6 grid gap-4">
          <label className="grid gap-2 text-sm font-semibold text-slate-800">District
            <select value={profile.district} onChange={(event) => update("district", event.target.value)} className="min-h-11 rounded-md border border-slate-200 px-3">
              {districts.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="grid gap-2 text-sm font-semibold text-slate-800">Monthly income
              <input type="number" min="0" value={profile.income ?? ""} onChange={(event) => update("income", Number(event.target.value))} className="min-h-11 rounded-md border border-slate-200 px-3" />
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-800">Land acres
              <input type="number" min="0" value={profile.land ?? ""} onChange={(event) => update("land", Number(event.target.value))} className="min-h-11 rounded-md border border-slate-200 px-3" />
            </label>
          </div>
          <label className="grid gap-2 text-sm font-semibold text-slate-800">Location
            <select value={profile.location} onChange={(event) => update("location", event.target.value as "rural" | "urban")} className="min-h-11 rounded-md border border-slate-200 px-3">
              <option value="rural">Rural</option>
              <option value="urban">Urban</option>
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-800">Electricity units
            <input type="number" min="0" value={profile.electricity_units ?? ""} onChange={(event) => update("electricity_units", Number(event.target.value))} className="min-h-11 rounded-md border border-slate-200 px-3" />
          </label>
          <div className="grid gap-3">
            {([
              ["has_rice_card", "Rice card"],
              ["has_ration_card", "Ration card"],
              ["farmer", "Farmer"],
              ["student", "Student"],
              ["widow", "Widow"],
              ["disabled", "Person with disability"],
              ["four_wheeler", "Owns four-wheeler"],
            ] as const).map(([key, label]) => (
              <label key={key} className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-800">
                {label}
                <input type="checkbox" checked={Boolean(profile[key])} onChange={(event) => update(key, event.target.checked)} className="h-5 w-5 accent-primary" />
              </label>
            ))}
          </div>
          <Button type="submit" disabled={loading}>Check Eligibility</Button>
        </form>
      </Card>
      <div className="space-y-4">
        {loading ? <><SkeletonCard /><SkeletonCard /><SkeletonCard /></> : null}
        {error ? <ErrorState message={error} /> : null}
        {!loading && !error && !result ? (
          <Card>
            <h2 className="text-xl font-bold text-slate-950">Results will appear here</h2>
            <p className="mt-2 text-slate-600">Submit the form to see eligible schemes, missing information, reasons, benefits, documents, and application links.</p>
          </Card>
        ) : null}
        {!loading && result ? groups.map((group) => (
          <Card key={group.key} className={group.tone}>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-950">{group.title}</h2>
              <span className="rounded-md bg-white px-2 py-1 text-sm font-bold text-slate-700">{group.items.length}</span>
            </div>
            <div className="grid gap-3">
              {group.items.length ? group.items.map((decision) => (
                <Accordion key={decision.scheme_id} title={decisionTitle(decision)}>
                  <div className="grid gap-4">
                    <Section title="Reasons" items={decision.reasons} />
                    <Section title="Benefits" items={decision.benefits} />
                    <Section title="Required documents" items={decision.missing_documents} />
                    <Section title="More information needed" items={[...decision.missing_information, ...decision.next_questions]} />
                    {decision.processing_time ? <p><strong>Processing time:</strong> {decision.processing_time}</p> : null}
                    {decision.application_links.length ? (
                      <div className="flex flex-wrap gap-2">
                        {decision.application_links.map((link) => (
                          <a key={link} href={link} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-semibold text-white">
                            Apply <ExternalLink className="h-4 w-4" />
                          </a>
                        ))}
                      </div>
                    ) : null}
                  </div>
                </Accordion>
              )) : <p className="rounded-md bg-white p-4 text-sm text-slate-600">No schemes in this group for the submitted profile.</p>}
            </div>
          </Card>
        )) : null}
      </div>
    </section>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <h3 className="font-bold text-slate-900">{title}</h3>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
