export default function Skeleton({ variant = 'card' }) {
  if (variant === 'hero') {
    return (
      <div className="w-full h-80 sm:h-96 rounded-2xl bg-surface-2 animate-pulse" />
    );
  }

  if (variant === 'text') {
    return (
      <div className="space-y-2 animate-pulse">
        <div className="h-4 bg-surface-2 rounded w-3/4" />
        <div className="h-4 bg-surface-2 rounded w-1/2" />
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className="rounded-xl bg-surface animate-pulse h-20 w-full" />
    );
  }

  return (
    <div className="rounded-xl overflow-hidden bg-surface animate-pulse">
      <div className="aspect-video bg-surface-2" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-surface-2 rounded w-3/4" />
        <div className="h-3 bg-surface-2 rounded w-1/2" />
        <div className="h-3 bg-surface-2 rounded w-1/3" />
      </div>
    </div>
  );
}
