import { isValidElement } from 'react';
import { PackageSearch } from 'lucide-react';

export default function EmptyState({ text = 'No hay resultados', icon: Icon = PackageSearch }) {
  let iconNode;
  if (isValidElement(Icon)) {
    iconNode = Icon;
  } else {
    iconNode = <Icon className="w-10 h-10 text-text-muted" />;
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <div className="text-text-muted">{iconNode}</div>
      <p className="text-text-muted">{text}</p>
    </div>
  );
}
