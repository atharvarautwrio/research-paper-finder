import React, { useState } from 'react';
import { Sliders, RotateCcw, ChevronDown, ChevronUp, Zap, Sparkles } from 'lucide-react';
import type { RankingWeights } from '../types';

interface WeightTunerProps {
  weights: RankingWeights;
  onChange: (weights: RankingWeights) => void;
  onApply: () => void;
}

const DEFAULT_WEIGHTS: RankingWeights = {
  bm25: 0.35,
  tfidf: 0.15,
  semantic: 0.35,
  title_match: 0.10,
  recency: 0.03,
  citations: 0.02
};

export const WeightTuner: React.FC<WeightTunerProps> = ({
  weights,
  onChange,
  onApply
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSliderChange = (key: keyof RankingWeights, value: number) => {
    onChange({
      ...weights,
      [key]: value
    });
  };

  const applyPreset = (presetWeights: RankingWeights) => {
    onChange(presetWeights);
  };

  return (
    <div className="weight-tuner-card">
      <button
        type="button"
        className="weight-tuner-header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="header-left">
          <Sliders className="tuner-icon" />
          <span className="tuner-title">Hybrid Ranking Weights Tuner</span>
          <span className="tuner-badge">
            Semantic: {Math.round(weights.semantic * 100)}% | BM25: {Math.round(weights.bm25 * 100)}% | Title: {Math.round(weights.title_match * 100)}%
          </span>
        </div>
        <div className="header-right">
          <span className="tuner-toggle-text">{isOpen ? 'Hide Weights' : 'Adjust Weights'}</span>
          {isOpen ? <ChevronUp className="chevron" /> : <ChevronDown className="chevron" />}
        </div>
      </button>

      {isOpen && (
        <div className="weight-tuner-body">
          {/* Presets Bar */}
          <div className="presets-bar">
            <span className="presets-label">
              <Zap className="preset-icon" /> Presets:
            </span>
            <button
              type="button"
              className="preset-btn"
              onClick={() => applyPreset(DEFAULT_WEIGHTS)}
            >
              Balanced Default
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() =>
                applyPreset({
                  bm25: 0.15,
                  tfidf: 0.05,
                  semantic: 0.65,
                  title_match: 0.10,
                  recency: 0.03,
                  citations: 0.02
                })
              }
            >
              <Sparkles className="btn-spark" /> Semantic Heavy
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() =>
                applyPreset({
                  bm25: 0.55,
                  tfidf: 0.25,
                  semantic: 0.10,
                  title_match: 0.10,
                  recency: 0.0,
                  citations: 0.0
                })
              }
            >
              Exact Lexical (BM25)
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() =>
                applyPreset({
                  bm25: 0.25,
                  tfidf: 0.10,
                  semantic: 0.30,
                  title_match: 0.05,
                  recency: 0.25,
                  citations: 0.05
                })
              }
            >
              Recent Publications
            </button>
            <button
              type="button"
              className="preset-btn"
              onClick={() =>
                applyPreset({
                  bm25: 0.20,
                  tfidf: 0.10,
                  semantic: 0.30,
                  title_match: 0.05,
                  recency: 0.05,
                  citations: 0.30
                })
              }
            >
              High Citation Impact
            </button>
          </div>

          {/* Sliders Grid */}
          <div className="sliders-grid">
            {/* Semantic Dense */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">Dense Semantic Similarity</span>
                <span className="slider-value">{Math.round(weights.semantic * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.semantic}
                onChange={(e) => handleSliderChange('semantic', parseFloat(e.target.value))}
                className="custom-range range-semantic"
              />
              <span className="slider-help">384-d bi-encoder transformer embeddings</span>
            </div>

            {/* BM25 Lexical */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">BM25 Lexical Term Density</span>
                <span className="slider-value">{Math.round(weights.bm25 * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.bm25}
                onChange={(e) => handleSliderChange('bm25', parseFloat(e.target.value))}
                className="custom-range range-bm25"
              />
              <span className="slider-help">Field-boosted Okapi probabilistic term score</span>
            </div>

            {/* TF-IDF */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">TF-IDF Vector Space</span>
                <span className="slider-value">{Math.round(weights.tfidf * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.tfidf}
                onChange={(e) => handleSliderChange('tfidf', parseFloat(e.target.value))}
                className="custom-range range-tfidf"
              />
              <span className="slider-help">Sparse cosine similarity on sublinear term freqs</span>
            </div>

            {/* Title Match */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">Title Exact Overlap</span>
                <span className="slider-value">{Math.round(weights.title_match * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.title_match}
                onChange={(e) => handleSliderChange('title_match', parseFloat(e.target.value))}
                className="custom-range range-title"
              />
              <span className="slider-help">Direct query concept appearance in title</span>
            </div>

            {/* Recency Prior */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">Recency Prior</span>
                <span className="slider-value">{Math.round(weights.recency * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={weights.recency}
                onChange={(e) => handleSliderChange('recency', parseFloat(e.target.value))}
                className="custom-range range-recency"
              />
              <span className="slider-help">Boosts newly published papers (2023-2025)</span>
            </div>

            {/* Citation Prior */}
            <div className="slider-group">
              <div className="slider-label-row">
                <span className="slider-name">Citation Impact Prior</span>
                <span className="slider-value">{Math.round(weights.citations * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={weights.citations}
                onChange={(e) => handleSliderChange('citations', parseFloat(e.target.value))}
                className="custom-range range-citations"
              />
              <span className="slider-help">Log-scaled citation authority weight</span>
            </div>
          </div>

          {/* Action Row */}
          <div className="tuner-action-row">
            <button
              type="button"
              className="reset-weights-btn"
              onClick={() => onChange(DEFAULT_WEIGHTS)}
            >
              <RotateCcw className="btn-icon" /> Reset to Defaults
            </button>
            <button
              type="button"
              className="apply-weights-btn"
              onClick={onApply}
            >
              Re-Rank Results with Custom Weights
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
