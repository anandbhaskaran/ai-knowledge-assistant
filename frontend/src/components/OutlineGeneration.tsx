import { useState } from 'react';
import { FileText, AlertCircle, ArrowLeft, CheckCircle2, List } from 'lucide-react';
import { generateOutline } from '../services/api';
import type { Idea, OutlineResponse } from '../types/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

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
    <div className="space-y-8 animate-fade-in">
      <Button
        onClick={onBack}
        variant="ghost"
        className="group gap-2"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        Back to Ideas
      </Button>

      <Card className="border-none shadow-xl bg-gradient-to-br from-white to-gray-50/50">
        <CardHeader className="space-y-3 pb-4">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl">
              <List className="h-7 w-7 text-primary" strokeWidth={2} />
            </div>
            <div className="flex-1">
              <CardTitle className="text-2xl">Create Article Outline</CardTitle>
              <CardDescription className="text-base mt-2">
                We'll structure your article with clear sections and verified sources.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="p-5 bg-gradient-to-br from-primary/5 to-primary/[0.02] rounded-xl border border-primary/10">
              <div className="flex items-center gap-2 mb-3">
                <Badge className="text-xs">Headline</Badge>
              </div>
              <h3 className="text-xl font-bold text-gray-900">{idea.headline}</h3>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-gray-900">Thesis Statement</h3>
              </div>
              <div className="bg-gray-50/80 rounded-lg p-4 border border-gray-200/60">
                <p className="text-gray-700 leading-relaxed">{idea.thesis}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-gray-900">Key Facts</h3>
                <Badge variant="secondary">{idea.key_facts.length}</Badge>
              </div>
              <ul className="space-y-2.5 bg-gray-50/50 rounded-lg p-4 border border-gray-200/40">
                {idea.key_facts.map((fact, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <CheckCircle2 className="text-primary flex-shrink-0 mt-0.5" size={16} strokeWidth={2.5} />
                    <span className="text-sm text-gray-700 leading-relaxed">{fact}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3 animate-slide-up">
              <AlertCircle className="text-destructive flex-shrink-0 mt-0.5" size={20} />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <Button
            onClick={handleGenerate}
            disabled={loading}
            size="lg"
            className="w-full text-base shadow-lg hover:shadow-xl"
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
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
