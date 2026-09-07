import React, { useState } from 'react';
import {
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  FileText,
  Sparkles,
  Award,
  Calendar,
  Layers,
  ChevronRight,
  GitFork
} from 'lucide-react';
import type { SearchResultItem } from '../types';

interface PaperCardProps {
  paper: SearchResultItem;
  onExplain: (paper: SearchResultItem) => void;
  onViewDetails: (paperId: string) => void;
  onFindSimilar: (paperId: string) => void;
  isSaved: boolean;
  onToggleSave: (paperId: string) => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  onExplain,
  onViewDetails,
  onFindSimilar,
  isSaved,
  onToggleSave
}) => {
  const [isAbstractExpanded, setIsAbstractExpanded] = useState(false);

  const relevancePct = paper.explanation?.relevance_percentage || Math.round((paper.explanation?.relevance_score ?? 0.85) * 100) || 85;

  // Determine relevance badge color
  const getBadgeClass = (pct: number) => {
    if (pct >= 85) return 'rel-high';
    if (pct >= 65) return 'rel-med';
    return 'rel-low';
  };

  const truncatedAbstract = paper.abstract.length > 280
    ? `${paper.abstract.substring(0, 280)}...`
    : paper.abstract;

  return (
    <article className="paper-card">
      {/* Top Metadata Row */}
      <div className="card-top-row">
        <div className="card-meta-left">
          <span className="rank-badge">#{paper.rank}</span>
          <span className="category-pill">{paper.primary_category}</span>
          <span className="meta-item">
            <Calendar className="meta-icon" /> {paper.publication_year}
          </span>
          <span className="meta-item venue-pill" title={paper.venue}>
            <Layers className="meta-icon" /> {paper.venue}
          </span>
        </div>

        <div className="card-meta-right">
          {/* Citation badge */}
          <div className="citation-pill" title={`${paper.citation_count.toLocaleString()} citations`}>
            <Award className="cit-icon" />
            <span>{paper.citation_count.toLocaleString()} citations</span>
          </div>

          {/* Relevance Match Meter */}
          <button
            type="button"
            className={`relevance-meter-btn ${getBadgeClass(relevancePct)}`}
            onClick={() => onExplain(paper)}
            title="Click to inspect transparent match signals breakdown"
          >
            <Sparkles className="rel-spark-icon" />
            <span className="rel-value">{relevancePct}% Match</span>
          </button>

          {/* Bookmark Button */}
          <button
            type="button"
            className={`bookmark-btn ${isSaved ? 'saved' : ''}`}
            onClick={() => onToggleSave(paper.paper_id)}
            title={isSaved ? 'Remove from Saved Papers' : 'Bookmark this Paper'}
          >
            {isSaved ? <BookmarkCheck className="bm-icon saved" /> : <Bookmark className="bm-icon" />}
          </button>
        </div>
      </div>

      {/* Paper Title */}
      <h3 className="paper-title" onClick={() => onViewDetails(paper.paper_id)}>
        {paper.title}
      </h3>

      {/* Authors */}
      <div className="paper-authors">
        {paper.authors.map((author, idx) => (
          <span key={idx} className="author-name">
            {author}{idx < paper.authors.length - 1 ? ',' : ''}
          </span>
        ))}
      </div>

      {/* Abstract */}
      <p className="paper-abstract">
        {isAbstractExpanded ? paper.abstract : truncatedAbstract}
        {paper.abstract.length > 280 && (
          <button
            type="button"
            className="toggle-abstract-btn"
            onClick={() => setIsAbstractExpanded(!isAbstractExpanded)}
          >
            {isAbstractExpanded ? ' Show less' : ' Read more'}
          </button>
        )}
      </p>

      {/* Keywords */}
      {paper.keywords && paper.keywords.length > 0 && (
        <div className="paper-keywords">
          {paper.keywords.slice(0, 5).map((kw, idx) => (
            <span key={idx} className="keyword-chip">
              {kw}
            </span>
          ))}
        </div>
      )}

      {/* Footer Action Buttons */}
      <div className="card-footer">
        <div className="footer-actions-left">
          <button
            type="button"
            className="action-btn explain-btn"
            onClick={() => onExplain(paper)}
          >
            <Sparkles className="btn-icon" />
            <span>Why this matched?</span>
          </button>

          <button
            type="button"
            className="action-btn similar-btn"
            onClick={() => onFindSimilar(paper.paper_id)}
          >
            <GitFork className="btn-icon" />
            <span>Similar Papers</span>
          </button>
        </div>

        <div className="footer-actions-right">
          {paper.doi && (
            <a
              href={`https://doi.org/${paper.doi}`}
              target="_blank"
              rel="noopener noreferrer"
              className="link-btn doi-btn"
            >
              <span>DOI</span>
              <ExternalLink className="link-icon" />
            </a>
          )}
          {paper.pdf_url && (
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="link-btn pdf-btn"
            >
              <FileText className="link-icon" />
              <span>PDF</span>
            </a>
          )}
          <button
            type="button"
            className="action-btn details-btn"
            onClick={() => onViewDetails(paper.paper_id)}
          >
            <span>Details</span>
            <ChevronRight className="chevron-icon" />
          </button>
        </div>
      </div>
    </article>
  );
};
