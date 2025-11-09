import { useState } from 'react';
import { FileEdit, AlertCircle, ArrowLeft, Download } from 'lucide-react';
import { generateDraft } from '../services/api';
import type { OutlineResponse, DraftResponse } from '../types/api';

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
    <div className="space-y-8">
      <button
        onClick={onBack}
        className="group flex items-center gap-2 text-gray-600 hover:text-[#980000] transition-colors font-medium"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        Back to Outline
      </button>

      <div className="bg-white rounded-2xl card-shadow p-8 border border-gray-100">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Draft Article</h2>
          <p className="text-gray-600">Convert your outline into a publication-ready draft.</p>
        </div>

        <div className="space-y-6 mb-8">
          <div className="p-4 bg-gradient-to-br from-[#FFF4F3] to-white rounded-xl border border-[#980000]/5">
            <h3 className="text-sm font-semibold text-[#980000] mb-2">Headline</h3>
            <p className="font-medium text-gray-900">{outline.headline}</p>
            <p className="text-sm text-gray-600 mt-2">{outline.thesis}</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <label htmlFor="wordCount" className="text-sm font-semibold text-gray-900">
                Target Length
              </label>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-[#FFF4F3] text-[#980000]">{targetWordCount.toLocaleString()} words</span>
            </div>
            <input
              type="range"
              id="wordCount"
              min="1000"
              max="2000"
              step="100"
              value={targetWordCount}
              onChange={(e) => setTargetWordCount(Number(e.target.value))}
              className="w-full h-2.5 bg-gray-200 rounded-full appearance-none cursor-pointer checkbox-custom"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>1,000</span>
              <span>2,000</span>
            </div>
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
              <span>Generating Draft...</span>
            </>
          ) : (
            <>
              <FileEdit size={20} />
              <span>Generate Draft</span>
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

      {draft && (
        <div className="bg-white rounded-2xl card-shadow p-8 border border-gray-100 space-y-6 fade-in">
          <div className="flex items-center justify-between pb-6 border-b">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Your Draft Article</h3>
              <p className="text-sm text-gray-600 mt-1">Ready for editing and publication</p>
            </div>
            <button
              onClick={downloadDraft}
              className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-[#FFF4F3] rounded-lg transition-colors text-sm font-medium text-gray-900"
            >
              <Download size={18} />
              Download
            </button>
          </div>

          {draft.warning && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="text-sm text-amber-900">{draft.warning}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100/30 rounded-lg border border-blue-100">
              <div className="text-xs font-semibold text-blue-900 uppercase tracking-wide mb-1">Word Count</div>
              <div className="text-2xl font-bold text-blue-900">{draft.word_count.toLocaleString()}</div>
            </div>
            {draft.editorial_compliance_score !== undefined && (
              <div className="p-4 bg-gradient-to-br from-green-50 to-green-100/30 rounded-lg border border-green-100">
                <div className="text-xs font-semibold text-green-900 uppercase tracking-wide mb-1">Compliance Score</div>
                <div className="text-2xl font-bold text-green-900">{(draft.editorial_compliance_score * 100).toFixed(0)}%</div>
              </div>
            )}
          </div>

          <div className="prose-lg max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed text-base">
              {draft.draft}
            </div>
          </div>

          {draft.sources_used && draft.sources_used.length > 0 && (
            <div className="border-t pt-6">
              <h4 className="font-semibold text-gray-900 mb-4">Sources Cited</h4>
              <div className="grid gap-3">
                {draft.sources_used.map((source, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-[#980000] transition-colors">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">{source.title}</div>
                        <div className="text-xs text-gray-500 mt-1">{source.source} • {source.date}</div>
                      </div>
                      {source.citation_number && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-[#FFF4F3] text-[#980000]">[{source.citation_number}]</span>
                      )}
                    </div>
                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-sm text-[#980000] hover:underline break-all">
                      {source.url}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
