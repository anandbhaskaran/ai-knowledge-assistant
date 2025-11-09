import { useState } from 'react';
import { Lightbulb, List, FileEdit } from 'lucide-react';
import Header from './components/Header';
import IdeaGeneration from './components/IdeaGeneration';
import OutlineGeneration from './components/OutlineGeneration';
import DraftGeneration from './components/DraftGeneration';
import type { Idea, OutlineResponse } from './types/api';

type Step = 'ideas' | 'outline' | 'draft';

function App() {
  const [step, setStep] = useState<Step>('ideas');
  const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);
  const [generatedOutline, setGeneratedOutline] = useState<OutlineResponse | null>(null);

  const handleIdeaSelected = (idea: Idea) => {
    setSelectedIdea(idea);
    setStep('outline');
  };

  const handleOutlineGenerated = (outline: OutlineResponse) => {
    setGeneratedOutline(outline);
    setStep('draft');
  };

  const handleBackToIdeas = () => {
    setStep('ideas');
    setSelectedIdea(null);
    setGeneratedOutline(null);
  };

  const handleBackToOutline = () => {
    setStep('outline');
    setGeneratedOutline(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FFF4F3] to-white">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <div className="flex items-center justify-center gap-3 sm:gap-6 px-4 py-3 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm">
            <StepIndicator
              active={step === 'ideas'}
              completed={step !== 'ideas'}
              icon={<Lightbulb size={16} strokeWidth={2} />}
              label="Ideas"
            />
            <div className="h-px w-8 sm:w-16 bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300" />
            <StepIndicator
              active={step === 'outline'}
              completed={step === 'draft'}
              icon={<List size={16} strokeWidth={2} />}
              label="Outline"
            />
            <div className="h-px w-8 sm:w-16 bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300" />
            <StepIndicator
              active={step === 'draft'}
              completed={false}
              icon={<FileEdit size={16} strokeWidth={2} />}
              label="Draft"
            />
          </div>
        </div>

        {step === 'ideas' && <IdeaGeneration onIdeaSelected={handleIdeaSelected} />}

        {step === 'outline' && selectedIdea && (
          <OutlineGeneration
            idea={selectedIdea}
            onOutlineGenerated={handleOutlineGenerated}
            onBack={handleBackToIdeas}
          />
        )}

        {step === 'draft' && generatedOutline && (
          <DraftGeneration
            outline={generatedOutline}
            onBack={handleBackToOutline}
          />
        )}
      </main>
    </div>
  );
}

interface StepIndicatorProps {
  active: boolean;
  completed: boolean;
  icon: React.ReactNode;
  label: string;
}

function StepIndicator({ active, completed, icon, label }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-300 ${
        active ? 'bg-[#980000] text-white shadow-md' :
        completed ? 'bg-green-500 text-white shadow-sm' :
        'bg-gray-200 text-gray-400'
      }`}>
        {completed ? (
          <div className="text-sm font-bold">✓</div>
        ) : (
          icon
        )}
      </div>
      <span className={`text-sm font-semibold transition-colors hidden sm:inline ${
        active ? 'text-[#980000]' : completed ? 'text-green-600' : 'text-gray-500'
      }`}>
        {label}
      </span>
    </div>
  );
}

export default App;
