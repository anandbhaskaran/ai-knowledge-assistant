import { useState, useEffect } from 'react';
import { Search, AlertCircle, Lightbulb, TrendingUp, DollarSign, Bitcoin, Cpu, Loader2 } from 'lucide-react';
import { generateIdeas } from '../services/api';
import type { IdeasResponse, Idea } from '../types/api';
import IdeaCard from './IdeaCard';
import IdeaCardSkeleton from './IdeaCardSkeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Badge } from './ui/Badge';

interface IdeaGenerationProps {
  onIdeaSelected: (idea: Idea) => void;
}

const TOPIC_CATEGORIES = [
  { label: 'Geopolitics', icon: TrendingUp, color: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' },
  { label: 'Macroeconomics', icon: DollarSign, color: 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100' },
  { label: 'Cryptocurrency', icon: Bitcoin, color: 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100' },
  { label: 'Technology', icon: Cpu, color: 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100' },
];

const LOADING_MESSAGES = [
  { message: "Searching archive sources...", icon: "🔍" },
  { message: "Analyzing relevant articles...", icon: "📚" },
  { message: "Generating article angles...", icon: "✨" },
  { message: "Verifying citations...", icon: "✓" },
  { message: "Almost done...", icon: "⏳" },
];

export default function IdeaGeneration({ onIdeaSelected }: IdeaGenerationProps) {
  const [topic, setTopic] = useState('');
  const [numIdeas, setNumIdeas] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IdeasResponse | null>(null);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  // Progressive loading messages and progress bar
  useEffect(() => {
    if (!loading) {
      setLoadingMessageIndex(0);
      setProgress(0);
      return;
    }

    const messageInterval = setInterval(() => {
      setLoadingMessageIndex((prev) => {
        if (prev < LOADING_MESSAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2000); // Change message every 2 seconds

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 95) {
          return prev + 1;
        }
        return prev;
      });
    }, 100); // Update progress every 100ms

    return () => {
      clearInterval(messageInterval);
      clearInterval(progressInterval);
    };
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLoadingMessageIndex(0);
    setProgress(0);

    try {
      const response = await generateIdeas(topic, numIdeas);
      setProgress(100);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (category: string) => {
    setTopic(category);
  };

  const handleIdeateFurther = async (idea: Idea) => {
    setTopic(idea.headline);
    setLoading(true);
    setError(null);
    setLoadingMessageIndex(0);
    setProgress(0);

    try {
      const response = await generateIdeas(idea.headline, numIdeas);
      setProgress(100);
      setResult(response);
      // Scroll to results
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <Card className="border-none shadow-xl bg-gradient-to-br from-white to-gray-50/50">
        <CardHeader className="space-y-3 pb-4">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl">
              <Lightbulb className="h-7 w-7 text-primary" strokeWidth={2} />
            </div>
            <div className="flex-1">
              <CardTitle className="text-2xl">Start Your Research</CardTitle>
              <CardDescription className="text-base mt-2">
                Tell us your topic, and we'll generate compelling article ideas with verified sources.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Quick Start Categories
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {TOPIC_CATEGORIES.map((category) => {
                  const Icon = category.icon;
                  return (
                    <button
                      key={category.label}
                      type="button"
                      onClick={() => handleCategoryClick(category.label)}
                      disabled={loading}
                      className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${category.color} ${
                        topic === category.label ? 'ring-2 ring-offset-2 ring-primary' : ''
                      }`}
                    >
                      <Icon size={24} strokeWidth={2} />
                      <span className="text-xs font-semibold text-center">{category.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-3">
              <label htmlFor="topic" className="block text-sm font-semibold text-gray-900">
                Or enter your own topic
              </label>
              <Input
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Artificial Intelligence in Healthcare..."
                className="h-12 text-base"
                disabled={loading}
                required
              />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label htmlFor="numIdeas" className="block text-sm font-semibold text-gray-900">
                  How many ideas?
                </label>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                  {numIdeas} idea{numIdeas !== 1 ? 's' : ''}
                </Badge>
              </div>
              <input
                type="range"
                id="numIdeas"
                min="1"
                max="5"
                value={numIdeas}
                onChange={(e) => setNumIdeas(Number(e.target.value))}
                disabled={loading}
                className="w-full h-2.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1</span>
                <span>5</span>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3 animate-slide-up">
                <AlertCircle className="text-destructive flex-shrink-0 mt-0.5" size={20} />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            {loading && (
              <div className="space-y-4 p-5 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 rounded-xl border border-blue-200/50 animate-slide-up">
                <div className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 text-primary animate-spin" />
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900">
                      <span className="mr-2">{LOADING_MESSAGES[loadingMessageIndex].icon}</span>
                      {LOADING_MESSAGES[loadingMessageIndex].message}
                    </p>
                  </div>
                  <span className="text-xs font-medium text-gray-600">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-primary to-primary/80 h-2 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              size="lg"
              className="w-full text-base shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Generating Ideas...</span>
                </>
              ) : (
                <>
                  <Search size={20} />
                  <span>Generate Ideas</span>
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-6 animate-slide-up">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-gray-900">Generating Ideas</h3>
              <Badge variant="secondary">
                <Loader2 className="h-3 w-3 animate-spin" />
              </Badge>
            </div>
            <div className="grid gap-5">
              {Array.from({ length: numIdeas }).map((_, index) => (
                <IdeaCardSkeleton key={index} />
              ))}
            </div>
          </div>
        </div>
      )}

      {!loading && result && (
        <div className="space-y-6 animate-slide-up">
          {result.warning && (
            <Card className="border-amber-200 bg-amber-50/50">
              <CardContent className="pt-6">
                <p className="text-sm text-amber-900">{result.warning}</p>
              </CardContent>
            </Card>
          )}

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-gray-900">Generated Ideas</h3>
              <Badge variant="secondary">{result.ideas.length}</Badge>
            </div>
            <div className="grid gap-5">
              {result.ideas.map((idea, index) => (
                <IdeaCard
                  key={index}
                  idea={idea}
                  onSelect={() => onIdeaSelected(idea)}
                  onIdeateFurther={() => handleIdeateFurther(idea)}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
