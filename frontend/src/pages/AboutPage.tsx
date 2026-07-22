import { Bot, CheckCircle2, FileSearch, ShieldCheck } from "lucide-react";
import { Card } from "../components/ui/Card";

const items = [
  { title: "Built for citizens", text: "Plain-language search helps students, farmers, senior citizens, women, job seekers, and families find relevant services.", icon: FileSearch },
  { title: "Grounded answers", text: "The assistant uses the backend knowledge base and source retrieval for service questions.", icon: Bot },
  { title: "Eligibility support", text: "Scheme checks are classified as eligible, need more information, or not eligible with clear reasons.", icon: CheckCircle2 },
  { title: "Official-first links", text: "Portal links are returned from the backend registry and opened as external government resources.", icon: ShieldCheck },
];

export default function AboutPage() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="max-w-3xl">
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-primary">About</p>
        <h1 className="mt-3 text-3xl font-extrabold text-slate-950 sm:text-4xl">A simple government service assistant for Andhra Pradesh</h1>
        <p className="mt-4 text-lg leading-8 text-slate-600">Yojana Autopilot connects citizens to services, schemes, offices, and official portals using the project backend as the source of truth.</p>
      </div>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.title}>
              <Icon className="h-7 w-7 text-primary" aria-hidden="true" />
              <h2 className="mt-4 text-lg font-bold text-slate-950">{item.title}</h2>
              <p className="mt-2 leading-7 text-slate-600">{item.text}</p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
