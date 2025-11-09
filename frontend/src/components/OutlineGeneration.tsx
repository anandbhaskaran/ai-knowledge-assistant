import { useState, useEffect } from 'react';
import { FileText, AlertCircle, ArrowLeft, CheckCircle2, List, Loader2, Globe, Edit3, Eye, ExternalLink, ArrowRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { generateOutline } from '../services/api';
import type { Idea, OutlineResponse } from '../types/api';
import OutlineResultSkeleton from './OutlineResultSkeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

interface OutlineGenerationProps {
  idea: Idea;
  onOutlineGenerated: (outline: OutlineResponse) => void;
  onBack: () => void;
}

const LOADING_MESSAGES = [
  { message: "Analyzing your topic...", icon: "🔍" },
  { message: "Searching archive sources...", icon: "📚" },
  { message: "Fetching web sources...", icon: "🌐" },
  { message: "Structuring outline...", icon: "📝" },
  { message: "Ranking sources...", icon: "⭐" },
  { message: "Almost done...", icon: "⏳" },
];

export default function OutlineGeneration({ idea, onOutlineGenerated, onBack }: OutlineGenerationProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enableWebSearch, setEnableWebSearch] = useState(true);
  const [outlineResult, setOutlineResult] = useState<OutlineResponse | null>(null);
  const [editedOutline, setEditedOutline] = useState('');
  const [isEditing, setIsEditing] = useState(false);
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
    }, 2000);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 95) {
          return prev + 1;
        }
        return prev;
      });
    }, 100);

    return () => {
      clearInterval(messageInterval);
      clearInterval(progressInterval);
    };
  }, [loading]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setLoadingMessageIndex(0);
    setProgress(0);

    try {
      const response = await generateOutline({
        headline: idea.headline,
        thesis: idea.thesis,
        key_facts: idea.key_facts,
        suggested_visualization: idea.suggested_visualization,
        enable_web_search: enableWebSearch,
      });
      setProgress(100);
      setOutlineResult(response);
      setEditedOutline(response.outline);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleProceedToDraft = () => {
    if (outlineResult) {
      onOutlineGenerated({
        ...outlineResult,
        outline: editedOutline, // Use edited outline
      });
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

            <div className="p-4 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 rounded-xl border border-blue-200/50">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableWebSearch}
                  onChange={(e) => setEnableWebSearch(e.target.checked)}
                  disabled={loading}
                  className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-semibold text-gray-900">Enable Web Search</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-0.5">Include real-time web sources alongside archive articles</p>
                </div>
              </label>
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
            onClick={handleGenerate}
            disabled={loading}
            size="lg"
            className="w-full text-base shadow-lg hover:shadow-xl"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
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

      {loading && <OutlineResultSkeleton />}

      {!loading && outlineResult && (
        <div className="space-y-6 animate-slide-up">
          {outlineResult.warning && (
            <Card className="border-amber-200 bg-amber-50/50">
              <CardContent className="pt-6">
                <p className="text-sm text-amber-900">{outlineResult.warning}</p>
              </CardContent>
            </Card>
          )}

          <Card className="border-none shadow-xl">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <FileText className="h-6 w-6 text-primary" />
                    Your Article Outline
                  </CardTitle>
                  <CardDescription className="mt-2">
                    Review and edit your outline before proceeding to draft generation
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setIsEditing(!isEditing)}
                    variant="outline"
                    size="sm"
                    className="gap-2"
                  >
                    {isEditing ? (
                      <>
                        <Eye size={16} />
                        Preview
                      </>
                    ) : (
                      <>
                        <Edit3 size={16} />
                        Edit
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {isEditing ? (
                <div className="space-y-2">
                  <label htmlFor="outline" className="text-sm font-semibold text-gray-900">
                    Edit Outline (Markdown)
                  </label>
                  <textarea
                    id="outline"
                    value={editedOutline}
                    onChange={(e) => setEditedOutline(e.target.value)}
                    rows={20}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-sm font-mono resize-y"
                    placeholder="Edit your outline here..."
                  />
                </div>
              ) : (
                <div className="prose prose-sm max-w-none bg-white rounded-lg border border-gray-200 p-6">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {editedOutline}
                  </ReactMarkdown>
                </div>
              )}
            </CardContent>
          </Card>

          {outlineResult.sources && outlineResult.sources.length > 0 && (
            <Card className="border-none shadow-xl">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                  Sources
                  <Badge variant="secondary">{outlineResult.sources.length}</Badge>
                </CardTitle>
                <CardDescription>
                  Verified sources used to generate this outline
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {outlineResult.sources.map((source, index) => (
                  <Card key={index} className="transition-all hover:shadow-md hover:border-primary/30">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-gray-900">{source.title}</h4>
                            <Badge variant={source.source_type === 'web' ? 'default' : 'secondary'} className="text-xs">
                              {source.source_type === 'web' ? (
                                <>
                                  <Globe className="h-3 w-3 mr-1" />
                                  Web
                                </>
                              ) : (
                                <>📚 Archive</>
                              )}
                            </Badge>
                          </div>
                          <div className="text-xs text-gray-500">{source.source} • {source.date}</div>
                        </div>
                        {source.relevance_score && (
                          <Badge variant="secondary" className="flex-shrink-0">
                            {(source.relevance_score * 100).toFixed(0)}% match
                          </Badge>
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
              </CardContent>
            </Card>
          )}

          <div className="flex justify-end">
            <Button
              onClick={handleProceedToDraft}
              size="lg"
              className="shadow-lg hover:shadow-xl group gap-2"
            >
              <span>Proceed to Draft Generation</span>
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
