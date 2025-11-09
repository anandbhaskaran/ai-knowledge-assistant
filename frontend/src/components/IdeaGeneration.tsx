import { useState } from 'react';
import { Search, AlertCircle } from 'lucide-react';
import { generateIdeas } from '../services/api';
import type { IdeasResponse, Idea } from '../types/api';
import IdeaCard from './IdeaCard';

interface IdeaGenerationProps {
  onIdeaSelected: (idea: Idea) => void;
}

export default function IdeaGeneration({ onIdeaSelected }: IdeaGenerationProps) {
  const [topic, setTopic] = useState('');
  const [numIdeas, setNumIdeas] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IdeasResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await generateIdeas(topic, numIdeas);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-2xl card-shadow p-8 border border-gray-100">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Start Your Research</h2>
          <p className="text-gray-600 mt-1">Tell us your topic, and we'll generate compelling article ideas with verified sources.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="topic" className="block text-sm font-semibold text-gray-900 mb-3">
              What's your topic?
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Artificial Intelligence in Healthcare..."
              className="w-full px-5 py-3.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#980000] focus:border-transparent outline-none transition-all text-base"
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <label htmlFor="numIdeas" className="block text-sm font-semibold text-gray-900">
                How many ideas?
              </label>
              <badge-primary className="badge-primary">{numIdeas} idea{numIdeas !== 1 ? 's' : ''}</badge-primary>
            </div>
            <input
              type="range"
              id="numIdeas"
              min="1"
              max="5"
              value={numIdeas}
              onChange={(e) => setNumIdeas(Number(e.target.value))}
              className="w-full h-2.5 bg-gray-200 rounded-full appearance-none cursor-pointer checkbox-custom"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>1</span>
              <span>5</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary-solid w-full disabled:bg-gray-300 disabled:cursor-not-allowed shadow-lg"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Generating Ideas...</span>
              </>
            ) : (
              <>
                <Search size={20} />
                <span>Generate Ideas</span>
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3 fade-in">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </div>

      {result && (
        <div className="space-y-6 fade-in">
          {result.warning && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p className="text-sm text-amber-900">{result.warning}</p>
            </div>
          )}

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Generated Ideas</h3>
            <div className="grid gap-5">
              {result.ideas.map((idea, index) => (
                <IdeaCard key={index} idea={idea} onSelect={() => onIdeaSelected(idea)} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
