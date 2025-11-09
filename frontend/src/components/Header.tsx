import { Sparkles } from 'lucide-react';
import Logo from './Logo';

export default function Header() {
  return (
    <header className="gradient-overlay text-white shadow-2xl border-b-4 border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between">
          <Logo />
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
            <Sparkles size={18} className="text-yellow-200" />
            <span className="text-sm font-medium">AI-Powered</span>
          </div>
        </div>
        <p className="text-base text-white/90 mt-6 max-w-2xl">
          Transform your research into publication-ready articles with AI-powered idea generation, structured outlines, and professional drafts.
        </p>
      </div>
    </header>
  );
}
