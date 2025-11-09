import { Lightbulb, CheckCircle2, ArrowRight } from 'lucide-react';
import type { Idea } from '../types/api';

interface IdeaCardProps {
  idea: Idea;
  onSelect: () => void;
}

export default function IdeaCard({ idea, onSelect }: IdeaCardProps) {
  return (
    <div className="card-hover bg-white border border-gray-100 rounded-xl p-6 card-shadow slide-up">
      <div className="flex items-start gap-3 mb-3">
        <div className="p-2.5 bg-gradient-to-br from-[#980000]/10 to-[#980000]/5 rounded-lg flex-shrink-0">
          <Lightbulb className="text-[#980000]" size={20} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 leading-tight flex-1">{idea.headline}</h3>
      </div>

      <p className="prose-content mb-4 text-gray-600">{idea.thesis}</p>

      <div className="mb-5 space-y-2.5">
        {idea.key_facts.map((fact, index) => (
          <div key={index} className="flex items-start gap-2.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#980000] mt-1.5 flex-shrink-0" />
            <p className="text-sm prose-content">{fact}</p>
          </div>
        ))}
      </div>

      {idea.suggested_visualization && (
        <div className="mb-5 p-4 bg-gradient-to-br from-[#FFF4F3] to-white rounded-lg border border-[#980000]/5">
          <p className="text-sm text-gray-700">
            <span className="font-semibold text-[#980000]">Visualization:</span> {idea.suggested_visualization}
          </p>
        </div>
      )}

      <button
        onClick={onSelect}
        className="btn-primary-solid w-full"
      >
        <CheckCircle2 size={18} />
        <span>Select Idea</span>
        <ArrowRight size={16} />
      </button>
    </div>
  );
}
