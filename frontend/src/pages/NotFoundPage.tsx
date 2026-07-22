import { Home } from "lucide-react";
import { Button } from "../components/ui/Button";

export default function NotFoundPage() {
  return (
    <section className="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center px-4 py-16 text-center">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-primary">404</p>
      <h1 className="mt-3 text-3xl font-extrabold text-slate-950">This page is not available</h1>
      <p className="mt-3 text-slate-600">The service page may have moved. Return home and search again.</p>
      <a href="/" className="mt-6">
        <Button icon={<Home className="h-4 w-4" />}>Go Home</Button>
      </a>
    </section>
  );
}
