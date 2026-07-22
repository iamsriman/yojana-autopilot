export function PageLoader() {
  return (
    <div className="mx-auto flex min-h-[50vh] max-w-6xl items-center justify-center px-4">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-primary" />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="shimmer mb-4 h-5 w-2/3 rounded" />
      <div className="shimmer mb-2 h-4 w-full rounded" />
      <div className="shimmer h-4 w-4/5 rounded" />
    </div>
  );
}

export function TypingIndicator() {
  return (
    <span className="inline-flex items-center gap-1" aria-label="Assistant is typing">
      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:120ms]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:240ms]" />
    </span>
  );
}
