import { Sparkles } from 'lucide-react';
import Logo from './Logo';

export default function Header() {
  return (
    <header className="gradient-overlay text-white shadow-lg border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <Logo />
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-full border border-white/20">
            <Sparkles size={16} className="text-yellow-200" />
            <span className="text-xs font-medium">AI-Powered</span>
          </div>
        </div>
      </div>
    </header>
  );
}
