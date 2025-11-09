import { useState, useEffect } from 'react';
import { FileEdit, AlertCircle, ArrowLeft, Download, FileText, ExternalLink, Globe, Loader2, Edit3, Eye, Copy, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { generateDraft } from '../services/api';
import type { OutlineResponse, DraftResponse } from '../types/api';
import DraftResultSkeleton from './DraftResultSkeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

interface DraftGenerationProps {
  outline: OutlineResponse;
  onBack: () => void;
}

const LOADING_MESSAGES = [
  { message: "Analyzing outline structure...", icon: "📋" },
  { message: "Searching for sources...", icon: "🔍" },
  { message: "Writing introduction...", icon: "✍️" },
  { message: "Developing body sections...", icon: "📝" },
  { message: "Crafting conclusion...", icon: "🎯" },
  { message: "Adding citations...", icon: "📚" },
  { message: "Finalizing draft...", icon: "⏳" },
];

export default function DraftGeneration({ outline, onBack }: DraftGenerationProps) {
  const [targetWordCount, setTargetWordCount] = useState(1500);
  const [enableWebSearch, setEnableWebSearch] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [editedDraft, setEditedDraft] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [copiedCitation, setCopiedCitation] = useState<number | null>(null);

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
    }, 120);

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
      const response = await generateDraft({
        headline: outline.headline,
        thesis: outline.thesis,
        outline: outline.outline,
        sources: outline.sources,
        key_facts: outline.key_facts,
        target_word_count: targetWordCount,
        enable_web_search: enableWebSearch,
      });
      setProgress(100);
      setDraft(response);
      setEditedDraft(response.draft);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const downloadDraft = () => {
    if (!draft) return;

    const content = `# ${draft.headline}\n\n${editedDraft}\n\n---\n\nWord Count: ${draft.word_count}\nEditorial Compliance Score: ${draft.editorial_compliance_score?.toFixed(2) || 'N/A'}`;
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

  const copyCitation = (citationNumber: number) => {
    const source = draft?.sources_used?.find(s => s.citation_number === citationNumber);
    if (source) {
      const citationText = `[${citationNumber}] ${source.title} - ${source.source} (${source.date})\n${source.url}`;
      navigator.clipboard.writeText(citationText);
      setCopiedCitation(citationNumber);
      setTimeout(() => setCopiedCitation(null), 2000);
    }
  };

  // Extract filename from citation for GitHub link
  const getGitHubLinkForSource = (citationNumber: number): string | null => {
    if (!draft) return null;

    // Find the citation in the original draft text
    const citationRegex = new RegExp(`\\[${citationNumber},\\s*([^,]+),\\s*([^,]+),\\s*([^\\]]+)\\]`);
    const match = draft.draft.match(citationRegex);

    if (match && match[1]) {
      const filename = match[1].trim();
      // Only create GitHub link for .txt files (archive sources)
      if (filename.endsWith('.txt')) {
        return `https://github.com/anandbhaskaran/ai-knowledge-assistant/blob/main/data/articles/${filename}`;
      }
    }
    return null;
  };

  // Replace citations in markdown with simple [n] format for rendering
  const preprocessMarkdown = (text: string): string => {
    // Replace [n, filename, title, date] with just [n]
    const citationRegex = /\[(\d+),\s*([^,]+),\s*([^,]+),\s*([^\]]+)\]/g;
    return text.replace(citationRegex, '[$1]');
  };

  // Custom component to render citations as clickable badges
  const CitationBadge = ({ citationNumber }: { citationNumber: number }) => (
    <sup>
      <button
        onClick={() => {
          const element = document.getElementById(`source-${citationNumber}`);
          element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          element?.classList.add('ring-2', 'ring-primary', 'ring-offset-2');
          setTimeout(() => {
            element?.classList.remove('ring-2', 'ring-primary', 'ring-offset-2');
          }, 2000);
        }}
        className="inline-flex items-center text-xs font-bold text-primary hover:text-primary/80 transition-colors cursor-pointer"
        title="Click to view source"
      >
        [{citationNumber}]
      </button>
    </sup>
  );

  // Render markdown and convert [n] to citation badges
  const renderMarkdownWithCitations = (text: string) => {
    const processedMarkdown = preprocessMarkdown(text);

    // Split by citation pattern [n] to insert custom components
    const parts: (string | JSX.Element)[] = [];
    const simpleCitationRegex = /\[(\d+)\]/g;
    let lastIndex = 0;
    let match;
    let key = 0;

    while ((match = simpleCitationRegex.exec(processedMarkdown)) !== null) {
      const citationNumber = parseInt(match[1]);

      // Add markdown content before citation
      if (match.index > lastIndex) {
        const markdownChunk = processedMarkdown.substring(lastIndex, match.index);
        parts.push(
          <ReactMarkdown key={`md-${key++}`} remarkPlugins={[remarkGfm]}>
            {markdownChunk}
          </ReactMarkdown>
        );
      }

      // Add citation badge
      parts.push(<CitationBadge key={`cite-${key++}`} citationNumber={citationNumber} />);

      lastIndex = match.index + match[0].length;
    }

    // Add remaining markdown
    if (lastIndex < processedMarkdown.length) {
      parts.push(
        <ReactMarkdown key={`md-${key++}`} remarkPlugins={[remarkGfm]}>
          {processedMarkdown.substring(lastIndex)}
        </ReactMarkdown>
      );
    }

    return parts;
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
                disabled={loading}
                className="w-full h-2.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1,000</span>
                <span>2,000</span>
              </div>
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
                  <p className="text-xs text-gray-600 mt-0.5">Include real-time web sources for the draft</p>
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

      {loading && <DraftResultSkeleton />}

      {!loading && draft && (
        <div className="space-y-6 animate-slide-up">
          {draft.warning && (
            <Card className="border-amber-200 bg-amber-50/50">
              <CardContent className="pt-6">
                <p className="text-sm text-amber-900">{draft.warning}</p>
              </CardContent>
            </Card>
          )}

          <Card className="border-none shadow-xl">
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <FileText className="h-6 w-6 text-primary" />
                    Your Draft Article
                  </CardTitle>
                  <CardDescription className="mt-2">
                    Review and edit your draft before publishing
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
                  <Button
                    onClick={downloadDraft}
                    variant="outline"
                    size="sm"
                    className="gap-2"
                  >
                    <Download size={16} />
                    Download
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
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

              {isEditing ? (
                <div className="space-y-2">
                  <label htmlFor="draft" className="text-sm font-semibold text-gray-900">
                    Edit Draft (Markdown)
                  </label>
                  <textarea
                    id="draft"
                    value={editedDraft}
                    onChange={(e) => setEditedDraft(e.target.value)}
                    rows={25}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-sm font-mono resize-y"
                    placeholder="Edit your draft here..."
                  />
                </div>
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <div className="prose prose-sm max-w-none">
                    {renderMarkdownWithCitations(editedDraft)}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {draft.sources_used && draft.sources_used.length > 0 && (
            <Card className="border-none shadow-xl">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                  Sources Cited
                  <Badge variant="secondary">{draft.sources_used.length}</Badge>
                </CardTitle>
                <CardDescription>
                  Click on citations in the text above to jump to sources
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {draft.sources_used.map((source, index) => (
                  <Card
                    key={index}
                    id={`source-${source.citation_number}`}
                    className="transition-all hover:shadow-md hover:border-primary/30"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {source.citation_number && (
                              <Badge className="flex-shrink-0">[{source.citation_number}]</Badge>
                            )}
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
                        <Button
                          onClick={() => copyCitation(source.citation_number!)}
                          variant="ghost"
                          size="sm"
                          className="gap-1 h-8"
                        >
                          {copiedCitation === source.citation_number ? (
                            <>
                              <CheckCircle size={14} className="text-green-600" />
                              <span className="text-xs">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy size={14} />
                              <span className="text-xs">Copy</span>
                            </>
                          )}
                        </Button>
                      </div>
                      <div className="space-y-2">
                        {source.citation_number && getGitHubLinkForSource(source.citation_number) && (
                          <a
                            href={getGitHubLinkForSource(source.citation_number)!}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline break-all flex items-center gap-1 group font-medium"
                          >
                            <span>📄 View article on Archive</span>
                            <ExternalLink size={12} className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </a>
                        )}
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-gray-600 hover:text-primary hover:underline break-all flex items-center gap-1 group"
                        >
                          <span>{source.url}</span>
                          <ExternalLink size={12} className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
