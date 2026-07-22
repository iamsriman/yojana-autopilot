import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./Button";
import { Card } from "./Card";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Card className="border-red-100 bg-red-50">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-danger" aria-hidden="true" />
          <div>
            <h2 className="font-semibold text-red-900">Unable to load this information</h2>
            <p className="mt-1 text-sm leading-6 text-red-800">{message}</p>
          </div>
        </div>
        {onRetry ? <Button variant="danger" icon={<RefreshCw className="h-4 w-4" />} onClick={onRetry}>Retry</Button> : null}
      </div>
    </Card>
  );
}
