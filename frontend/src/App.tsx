import { useState } from 'react';
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
        <div className="mb-12">
          <div className="flex items-center gap-2 sm:gap-4">
            <StepIndicator active={step === 'ideas'} completed={step !== 'ideas'} number={1} label="Ideas" />
            <div className="flex-1 h-1 bg-gradient-to-r from-gray-300 to-transparent" />
            <StepIndicator active={step === 'outline'} completed={step === 'draft'} number={2} label="Outline" />
            <div className="flex-1 h-1 bg-gradient-to-r from-gray-300 to-transparent" />
            <StepIndicator active={step === 'draft'} completed={false} number={3} label="Draft" />
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
  number: number;
  label: string;
}

function StepIndicator({ active, completed, number, label }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all duration-300 ${
        active ? 'bg-[#980000] text-white shadow-lg scale-100' :
        completed ? 'bg-green-500 text-white shadow-md' :
        'bg-gray-200 text-gray-500 shadow-sm'
      }`}>
        {completed ? '✓' : number}
      </div>
      <span className={`text-xs font-semibold uppercase tracking-wide hidden md:inline transition-colors ${
        active ? 'text-[#980000]' : completed ? 'text-green-600' : 'text-gray-400'
      }`}>
        {label}
      </span>
    </div>
  );
}

export default App;
