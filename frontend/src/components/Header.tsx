import { FileText, Sparkles } from 'lucide-react';

export default function Header() {
  return (
    <header className="gradient-overlay text-white shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/15 backdrop-blur-sm rounded-xl border border-white/20">
            <FileText size={32} strokeWidth={2} className="text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold tracking-tight">AI Journalist Assistant</h1>
              <Sparkles size={24} className="text-yellow-200" />
            </div>
            <p className="text-base text-white/85 mt-1">Transform your research into publication-ready articles</p>
          </div>
        </div>
      </div>
    </header>
  );
}
