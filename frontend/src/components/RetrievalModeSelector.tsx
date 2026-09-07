import React from 'react';
import type { RetrievalMode } from '../types';
import { Sparkles, Brain, FileText, BarChart2 } from 'lucide-react';

interface RetrievalModeSelectorProps {
  currentMode: RetrievalMode;
  onChange: (mode: RetrievalMode) => void;
}

export const RetrievalModeSelector: React.FC<RetrievalModeSelectorProps> = ({
  currentMode,
  onChange
}) => {
  const modes: {
    id: RetrievalMode;
    title: string;
    description: string;
    icon: React.ReactNode;
    tag?: string;
  }[] = [
    {
      id: 'hybrid',
      title: 'Hybrid Multi-Signal',
      description: 'Fuses Dense Vectors + BM25 Lexical + TF-IDF + Recency & Citations',
      icon: <Sparkles className="mode-icon" />,
      tag: 'Recommended'
    },
    {
      id: 'semantic',
      title: 'Dense Semantic',
      description: '384-d transformer embeddings matching deep research intent',
      icon: <Brain className="mode-icon" />
    },
    {
      id: 'bm25',
      title: 'Okapi BM25F',
      description: 'Field-boosted probabilistic lexical term frequency saturation',
      icon: <FileText className="mode-icon" />
    },
    {
      id: 'tfidf',
      title: 'TF-IDF Space',
      description: 'Sublinear term frequency cosine similarity vector model',
      icon: <BarChart2 className="mode-icon" />
    }
  ];

  return (
    <div className="retrieval-mode-container">
      <div className="retrieval-mode-tabs">
        {modes.map((m) => (
          <button
            key={m.id}
            type="button"
            className={`retrieval-mode-card ${currentMode === m.id ? 'active' : ''}`}
            onClick={() => onChange(m.id)}
          >
            <div className="mode-header">
              <span className="mode-icon-wrapper">{m.icon}</span>
              <span className="mode-title">{m.title}</span>
              {m.tag && <span className="mode-tag">{m.tag}</span>}
            </div>
            <p className="mode-desc">{m.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};
