import { Newspaper } from 'lucide-react';

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export default function Logo({ className = '', showText = true }: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="relative">
        <div className="absolute inset-0 bg-white/20 rounded-lg blur-sm"></div>
        <div className="relative bg-white rounded-lg p-2 shadow-lg">
          <Newspaper className="h-6 w-6 text-[#980000]" strokeWidth={2.5} />
        </div>
      </div>
      {showText && (
        <div className="flex flex-col">
          <span className="text-xl font-bold text-white tracking-tight">
            AI Journalist
          </span>
          <span className="text-xs text-white/80 font-medium -mt-1">
            Research Assistant
          </span>
        </div>
      )}
    </div>
  );
}
