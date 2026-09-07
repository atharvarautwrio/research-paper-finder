import React, { useState, useEffect } from 'react';
import {
  X,
  Calendar,
  Award,
  BookOpen,
  Layers,
  ExternalLink,
  FileText,
  Bookmark,
  BookmarkCheck,
  Sparkles,
  GitFork,
  ArrowRight
} from 'lucide-react';
import type { PaperDetail, PaperRecommendation } from '../types';
import { ApiService } from '../services/api';

interface PaperDetailModalProps {
  paperId: string | null;
  onClose: () => void;
  onSelectPaper: (paperId: string) => void;
  isSaved: boolean;
  onToggleSave: (paperId: string) => void;
}

export const PaperDetailModal: React.FC<PaperDetailModalProps> = ({
  paperId,
  onClose,
  onSelectPaper,
  isSaved,
  onToggleSave
}) => {
  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [recommendations, setRecommendations] = useState<PaperRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'recommendations'>('overview');

  useEffect(() => {
    if (!paperId) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [paperData, recsData] = await Promise.all([
          ApiService.getPaper(paperId),
          ApiService.getRecommendations(paperId, 6)
        ]);
        setPaper(paperData);
        setRecommendations(recsData);
      } catch (err) {
        console.error('Failed to load paper details:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [paperId]);

  if (!paperId) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container detail-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-left">
            <span className="category-pill">{paper?.primary_category || 'Academic Paper'}</span>
            <span className="meta-item">
              <Calendar className="meta-icon" /> {paper?.publication_year}
            </span>
            <span className="meta-item venue-pill">
              <Layers className="meta-icon" /> {paper?.venue}
            </span>
          </div>
          <div className="header-actions">
            {paper && (
              <button
                type="button"
                className={`bookmark-btn ${isSaved ? 'saved' : ''}`}
                onClick={() => onToggleSave(paper.paper_id)}
                title={isSaved ? 'Remove from Saved' : 'Save paper'}
              >
                {isSaved ? <BookmarkCheck className="bm-icon saved" /> : <Bookmark className="bm-icon" />}
              </button>
            )}
            <button type="button" className="modal-close-btn" onClick={onClose}>
              <X className="close-icon" />
            </button>
          </div>
        </div>

        {/* Modal Navigation */}
        <div className="modal-tabs-bar">
          <button
            type="button"
            className={`modal-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <BookOpen className="tab-icon" /> Paper Overview
          </button>
          <button
            type="button"
            className={`modal-tab ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            <GitFork className="tab-icon" /> Similar Recommendations ({recommendations.length})
          </button>
        </div>

        {/* Body */}
        <div className="modal-body scrollable">
          {loading ? (
            <div className="modal-loading-state">
              <div className="spinner"></div>
              <p>Fetching paper intelligence & dense recommendations...</p>
            </div>
          ) : paper ? (
            activeTab === 'overview' ? (
              <div className="overview-tab-content">
                <h1 className="detail-title">{paper.title}</h1>

                {/* Authors */}
                <div className="detail-authors">
                  {paper.authors.map((author, idx) => (
                    <span key={idx} className="author-tag">
                      {author}
                    </span>
                  ))}
                </div>

                {/* Metrics Pill Grid */}
                <div className="detail-metrics-grid">
                  <div className="metric-box">
                    <Award className="m-icon" />
                    <div className="m-info">
                      <span className="m-value">{paper.citation_count.toLocaleString()}</span>
                      <span className="m-label">Citations</span>
                    </div>
                  </div>
                  <div className="metric-box">
                    <Calendar className="m-icon" />
                    <div className="m-info">
                      <span className="m-value">{paper.publication_year}</span>
                      <span className="m-label">Publication Year</span>
                    </div>
                  </div>
                  <div className="metric-box">
                    <Layers className="m-icon" />
                    <div className="m-info">
                      <span className="m-value">{paper.venue}</span>
                      <span className="m-label">Venue</span>
                    </div>
                  </div>
                </div>

                {/* Abstract Section */}
                <div className="detail-section">
                  <h3 className="section-heading">Abstract</h3>
                  <p className="detail-abstract-text">{paper.abstract}</p>
                </div>

                {/* Keywords & Categories */}
                <div className="detail-section">
                  <h3 className="section-heading">Categories & Keywords</h3>
                  <div className="detail-chips-row">
                    {paper.categories.map((cat, i) => (
                      <span key={`cat-${i}`} className="category-chip">
                        {cat}
                      </span>
                    ))}
                    {paper.keywords.map((kw, i) => (
                      <span key={`kw-${i}`} className="keyword-chip">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>

                {/* External Links */}
                <div className="detail-links-row">
                  {paper.doi && (
                    <a
                      href={`https://doi.org/${paper.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ext-link-btn"
                    >
                      <ExternalLink className="btn-icon" />
                      <span>DOI: {paper.doi}</span>
                    </a>
                  )}
                  {paper.pdf_url && (
                    <a
                      href={paper.pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ext-link-btn primary"
                    >
                      <FileText className="btn-icon" />
                      <span>View / Download PDF</span>
                    </a>
                  )}
                </div>
              </div>
            ) : (
              /* Recommendations Tab */
              <div className="recommendations-tab-content">
                <div className="recs-intro-banner">
                  <Sparkles className="banner-icon" />
                  <div>
                    <h4 className="banner-title">Multi-Signal Paper Similarity Graph</h4>
                    <p className="banner-desc">
                      Ranked by fusing dense vector cosine similarity (45%), lexical TF-IDF overlap (25%), category alignment (15%), and author/venue graph edges (15%).
                    </p>
                  </div>
                </div>

                <div className="recs-grid">
                  {recommendations.map((rec) => (
                    <div key={rec.paper_id} className="rec-card">
                      <div className="rec-header">
                        <span className="rec-sim-badge">
                          {rec.similarity_percentage}% Similar
                        </span>
                        <span className="rec-year">{rec.publication_year}</span>
                      </div>

                      <h4
                        className="rec-title"
                        onClick={() => onSelectPaper(rec.paper_id)}
                      >
                        {rec.title}
                      </h4>

                      <p className="rec-authors">
                        {rec.authors.slice(0, 3).join(', ')}
                        {rec.authors.length > 3 ? ' et al.' : ''}
                      </p>

                      <p className="rec-abstract-preview">
                        {rec.abstract.substring(0, 140)}...
                      </p>

                      {/* Reasons */}
                      <div className="rec-reasons">
                        {rec.reasons.map((r, ri) => (
                          <span key={ri} className="rec-reason-pill">
                            {r}
                          </span>
                        ))}
                      </div>

                      <button
                        type="button"
                        className="pivot-paper-btn"
                        onClick={() => onSelectPaper(rec.paper_id)}
                      >
                        <span>Explore Paper</span>
                        <ArrowRight className="arrow-icon" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )
          ) : (
            <p>Paper not found.</p>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
