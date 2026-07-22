import { FormEvent } from "react";
import { Search } from "lucide-react";
import { Button } from "./Button";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit?: () => void;
  placeholder: string;
  label: string;
}

export function SearchBar({ value, onChange, onSubmit, placeholder, label }: SearchBarProps) {
  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit?.();
  }

  return (
    <form onSubmit={submit} role="search" className="flex w-full flex-col gap-3 sm:flex-row">
      <label className="sr-only" htmlFor="global-search">{label}</label>
      <div className="relative flex-1">
        <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <input
          id="global-search"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="min-h-12 w-full rounded-md border border-slate-200 bg-white py-3 pl-12 pr-4 text-base text-slate-900 shadow-sm placeholder:text-slate-400"
          placeholder={placeholder}
        />
      </div>
      <Button type="submit" icon={<Search className="h-4 w-4" />}>Search</Button>
    </form>
  );
}
