import { Lightbulb, CheckCircle2, ArrowRight, Image, Sparkles } from 'lucide-react';
import type { Idea } from '../types/api';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

interface IdeaCardProps {
  idea: Idea;
  onSelect: () => void;
  onIdeateFurther: () => void;
}

export default function IdeaCard({ idea, onSelect, onIdeateFurther }: IdeaCardProps) {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-xl hover:-translate-y-1 border-gray-200 animate-slide-up">
      <CardContent className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <div className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl flex-shrink-0">
            <Lightbulb className="text-primary h-6 w-6" strokeWidth={2} />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 leading-tight mb-2">{idea.headline}</h3>
            <p className="text-gray-600 leading-relaxed">{idea.thesis}</p>
          </div>
        </div>

        <div className="mb-4 space-y-2.5 bg-gray-50/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Badge variant="secondary" className="text-xs">Key Facts</Badge>
          </div>
          {idea.key_facts.map((fact, index) => (
            <div key={index} className="flex items-start gap-3">
              <CheckCircle2 className="text-primary mt-0.5 flex-shrink-0" size={16} strokeWidth={2.5} />
              <p className="text-sm text-gray-700 leading-relaxed">{fact}</p>
            </div>
          ))}
        </div>

        {idea.suggested_visualization && (
          <div className="mb-5 p-4 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 rounded-lg border border-blue-100/50">
            <div className="flex items-start gap-2.5">
              <Image className="text-blue-600 mt-0.5 flex-shrink-0" size={16} />
              <div>
                <p className="text-xs font-semibold text-blue-900 mb-1">Suggested Visualization</p>
                <p className="text-sm text-gray-700">{idea.suggested_visualization}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Button
            onClick={onIdeateFurther}
            variant="outline"
            size="lg"
            className="shadow-sm hover:shadow-md group"
          >
            <Sparkles size={18} />
            <span>Ideate Further</span>
          </Button>
          <Button
            onClick={onSelect}
            size="lg"
            className="shadow-md hover:shadow-lg group"
          >
            <span>Create Outline</span>
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
