import React from 'react';
import { X, Sparkles, Brain, FileText, BarChart2, CheckCircle2, Award, Calendar, Layers } from 'lucide-react';
import type { SearchResultItem } from '../types';

interface ExplainabilityModalProps {
  paper: SearchResultItem | null;
  onClose: () => void;
  query: string;
}

export const ExplainabilityModal: React.FC<ExplainabilityModalProps> = ({
  paper,
  onClose,
  query
}) => {
  if (!paper || !paper.explanation) return null;

  const exp = paper.explanation;
  const signals = exp.signals || {};

  const signalDefinitions = [
    {
      key: 'semantic',
      name: 'Dense Semantic Vector',
      desc: '384-d neural transformer conceptual intent match',
      icon: <Brain className="signal-icon semantic" />,
      value: signals.semantic ?? 0,
      color: 'var(--accent-primary)'
    },
    {
      key: 'bm25',
      name: 'BM25 Lexical Density',
      desc: 'Field-weighted probabilistic term saturation',
      icon: <FileText className="signal-icon bm25" />,
      value: signals.bm25 ?? 0,
      color: 'var(--color-emerald)'
    },
    {
      key: 'tfidf',
      name: 'TF-IDF Cosine Similarity',
      desc: 'Sparse sublinear term frequency overlap',
      icon: <BarChart2 className="signal-icon tfidf" />,
      value: signals.tfidf ?? 0,
      color: 'var(--color-amber)'
    },
    {
      key: 'title_match',
      name: 'Title Overlap Match',
      desc: 'Direct occurrence of query concepts in paper title',
      icon: <Layers className="signal-icon title" />,
      value: signals.title_match ?? 0,
      color: 'var(--color-purple)'
    },
    {
      key: 'recency',
      name: 'Recency Prior',
      desc: 'Normalized publication era boost (2015-2025)',
      icon: <Calendar className="signal-icon recency" />,
      value: signals.recency ?? 0,
      color: 'var(--color-cyan)'
    },
    {
      key: 'citations',
      name: 'Citation Impact Prior',
      desc: 'Log-normalized scholarly authority prior',
      icon: <Award className="signal-icon citations" />,
      value: signals.citations ?? 0,
      color: 'var(--color-indigo)'
    }
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container explain-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-left">
            <div className="modal-icon-badge">
              <Sparkles className="icon" />
            </div>
            <div>
              <h2 className="modal-title">Match Transparency & Explainability</h2>
              <p className="modal-subtitle">Transparent mathematical breakdown of retrieval signals</p>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X className="close-icon" />
          </button>
        </div>

        {/* Content Body */}
        <div className="modal-body scrollable">
          {/* Query & Target Paper Banner */}
          <div className="explain-target-box">
            <div className="target-item">
              <span className="target-label">Search Query:</span>
              <span className="target-query">"{query}"</span>
            </div>
            <div className="target-item">
              <span className="target-label">Retrieved Paper:</span>
              <span className="target-paper-title">{paper.title}</span>
            </div>
          </div>

          {/* Overall Match Score Banner */}
          <div className="overall-score-banner">
            <div className="score-details">
              <span className="score-label">Overall Relevancy Score</span>
              <div className="score-number-row">
                <span className="score-pct">{exp.relevance_percentage}%</span>
                <span className="score-raw">Normalized Index: {exp.relevance_score}</span>
              </div>
            </div>
            <div className="score-progress-bar-container">
              <div
                className="score-progress-bar"
                style={{ width: `${Math.min(exp.relevance_percentage, 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Signal Breakdown Section */}
          <div className="explain-section">
            <h3 className="section-title">Retrieval Signal Breakdown</h3>
            <div className="signals-grid">
              {signalDefinitions.map((sig) => {
                const pct = Math.round(sig.value * 100);
                return (
                  <div key={sig.key} className="signal-card">
                    <div className="signal-top">
                      <div className="sig-title-group">
                        {sig.icon}
                        <div>
                          <span className="sig-name">{sig.name}</span>
                          <span className="sig-desc">{sig.desc}</span>
                        </div>
                      </div>
                      <span className="sig-value-badge">{pct}%</span>
                    </div>
                    <div className="sig-bar-track">
                      <div
                        className="sig-bar-fill"
                        style={{
                          width: `${Math.min(pct, 100)}%`,
                          backgroundColor: sig.color
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Reasoning Bullet Points */}
          {exp.reasons && exp.reasons.length > 0 && (
            <div className="explain-section">
              <h3 className="section-title">Key Match Justifications</h3>
              <ul className="reasons-list">
                {exp.reasons.map((reason, idx) => (
                  <li key={idx} className="reason-item">
                    <CheckCircle2 className="reason-icon" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Matched & Expanded Terms */}
          <div className="explain-terms-row">
            {exp.matched_query_terms && exp.matched_query_terms.length > 0 && (
              <div className="terms-col">
                <span className="terms-col-title">Matched Query Terms:</span>
                <div className="terms-pills-list">
                  {exp.matched_query_terms.map((term, i) => (
                    <span key={i} className="term-pill matched">
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {exp.query_expansion_used && exp.query_expansion_used.length > 0 && (
              <div className="terms-col">
                <span className="terms-col-title">Domain Synonyms Matched:</span>
                <div className="terms-pills-list">
                  {exp.query_expansion_used.map((syn, i) => (
                    <span key={i} className="term-pill expanded">
                      + {syn}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
