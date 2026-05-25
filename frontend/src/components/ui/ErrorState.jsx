import { AlertCircle } from 'lucide-react';

export default function ErrorState({ message = 'Algo salió mal', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <AlertCircle className="w-10 h-10 text-danger" />
      <p className="text-text-muted max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-1 px-4 py-2 rounded-lg bg-surface-2 hover:bg-border text-text text-sm transition-colors cursor-pointer"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
