import { useState } from 'react';
import { FileText, AlertCircle, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { generateOutline } from '../services/api';
import type { Idea, OutlineResponse } from '../types/api';

interface OutlineGenerationProps {
  idea: Idea;
  onOutlineGenerated: (outline: OutlineResponse) => void;
  onBack: () => void;
}

export default function OutlineGeneration({ idea, onOutlineGenerated, onBack }: OutlineGenerationProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await generateOutline({
        headline: idea.headline,
        thesis: idea.thesis,
        key_facts: idea.key_facts,
        suggested_visualization: idea.suggested_visualization,
      });
      onOutlineGenerated(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <button
        onClick={onBack}
        className="group flex items-center gap-2 text-gray-600 hover:text-[#980000] transition-colors font-medium"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        Back to Ideas
      </button>

      <div className="bg-white rounded-2xl card-shadow p-8 border border-gray-100">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Article Outline</h2>
          <p className="text-gray-600">We'll structure your article with clear sections and sources.</p>
        </div>

        <div className="space-y-6 mb-8">
          <div className="p-4 bg-gradient-to-br from-[#FFF4F3] to-white rounded-xl border border-[#980000]/5">
            <h3 className="text-sm font-semibold text-[#980000] mb-2">Headline</h3>
            <p className="text-gray-900 font-medium">{idea.headline}</p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Thesis & Key Facts</h3>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 mb-4">
              <p className="text-gray-700 leading-relaxed">{idea.thesis}</p>
            </div>
            <ul className="space-y-2.5">
              {idea.key_facts.map((fact, index) => (
                <li key={index} className="flex items-start gap-2.5">
                  <CheckCircle2 className="text-[#980000] flex-shrink-0 mt-0.5" size={18} />
                  <span className="text-sm text-gray-700">{fact}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="btn-primary-solid w-full disabled:bg-gray-300 disabled:cursor-not-allowed shadow-lg"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Generating Outline...</span>
            </>
          ) : (
            <>
              <FileText size={20} />
              <span>Generate Outline</span>
            </>
          )}
        </button>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3 fade-in">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
