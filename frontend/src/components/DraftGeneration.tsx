import { useState } from 'react';
import { FileEdit, AlertCircle, ArrowLeft, Download, FileText, ExternalLink } from 'lucide-react';
import { generateDraft } from '../services/api';
import type { OutlineResponse, DraftResponse } from '../types/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

interface DraftGenerationProps {
  outline: OutlineResponse;
  onBack: () => void;
}

export default function DraftGeneration({ outline, onBack }: DraftGenerationProps) {
  const [targetWordCount, setTargetWordCount] = useState(1500);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<DraftResponse | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await generateDraft({
        headline: outline.headline,
        thesis: outline.thesis,
        outline: outline.outline,
        sources: outline.sources,
        key_facts: outline.key_facts,
        target_word_count: targetWordCount,
      });
      setDraft(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const downloadDraft = () => {
    if (!draft) return;

    const content = `# ${draft.headline}\n\n${draft.draft}\n\n---\n\nWord Count: ${draft.word_count}\nEditorial Compliance Score: ${draft.editorial_compliance_score?.toFixed(2) || 'N/A'}`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${draft.headline.toLowerCase().replace(/\s+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <Button
        onClick={onBack}
        variant="ghost"
        className="group gap-2"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        Back to Outline
      </Button>

      <Card className="border-none shadow-xl bg-gradient-to-br from-white to-gray-50/50">
        <CardHeader className="space-y-3 pb-4">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl">
              <FileEdit className="h-7 w-7 text-primary" strokeWidth={2} />
            </div>
            <div className="flex-1">
              <CardTitle className="text-2xl">Generate Draft Article</CardTitle>
              <CardDescription className="text-base mt-2">
                Convert your outline into a publication-ready draft with proper citations.
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
              <h3 className="text-xl font-bold text-gray-900 mb-2">{outline.headline}</h3>
              <p className="text-sm text-gray-600">{outline.thesis}</p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label htmlFor="wordCount" className="text-sm font-semibold text-gray-900">
                  Target Length
                </label>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                  {targetWordCount.toLocaleString()} words
                </Badge>
              </div>
              <input
                type="range"
                id="wordCount"
                min="1000"
                max="2000"
                step="100"
                value={targetWordCount}
                onChange={(e) => setTargetWordCount(Number(e.target.value))}
                className="w-full h-2.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1,000</span>
                <span>2,000</span>
              </div>
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
                <span>Generating Draft...</span>
              </>
            ) : (
              <>
                <FileEdit size={20} />
                <span>Generate Draft</span>
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {draft && (
        <Card className="border-none shadow-xl animate-slide-up">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <CardTitle className="text-2xl flex items-center gap-3">
                  <FileText className="h-6 w-6 text-primary" />
                  Your Draft Article
                </CardTitle>
                <CardDescription className="mt-2">
                  Ready for editing and publication
                </CardDescription>
              </div>
              <Button
                onClick={downloadDraft}
                variant="outline"
                className="gap-2"
              >
                <Download size={18} />
                Download
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {draft.warning && (
              <Card className="border-amber-200 bg-amber-50/50">
                <CardContent className="pt-6">
                  <p className="text-sm text-amber-900">{draft.warning}</p>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-5 bg-gradient-to-br from-blue-50 to-blue-100/30 rounded-xl border border-blue-200/50">
                <div className="text-xs font-semibold text-blue-900 uppercase tracking-wide mb-2">Word Count</div>
                <div className="text-3xl font-bold text-blue-900">{draft.word_count.toLocaleString()}</div>
              </div>
              {draft.editorial_compliance_score !== undefined && (
                <div className="p-5 bg-gradient-to-br from-green-50 to-green-100/30 rounded-xl border border-green-200/50">
                  <div className="text-xs font-semibold text-green-900 uppercase tracking-wide mb-2">Compliance Score</div>
                  <div className="text-3xl font-bold text-green-900">{(draft.editorial_compliance_score * 100).toFixed(0)}%</div>
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="prose prose-lg max-w-none">
                <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                  {draft.draft}
                </div>
              </div>
            </div>

            {draft.sources_used && draft.sources_used.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <h4 className="text-lg font-semibold text-gray-900">Sources Cited</h4>
                  <Badge variant="secondary">{draft.sources_used.length}</Badge>
                </div>
                <div className="grid gap-3">
                  {draft.sources_used.map((source, index) => (
                    <Card key={index} className="transition-all hover:shadow-md hover:border-primary/30">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900 mb-1">{source.title}</div>
                            <div className="text-xs text-gray-500">{source.source} • {source.date}</div>
                          </div>
                          {source.citation_number && (
                            <Badge className="flex-shrink-0">[{source.citation_number}]</Badge>
                          )}
                        </div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline break-all flex items-center gap-1 group"
                        >
                          <span>{source.url}</span>
                          <ExternalLink size={12} className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </a>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
