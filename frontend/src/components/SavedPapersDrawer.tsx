import React, { useState } from 'react';
import {
  Bookmark,
  Trash2,
  Download,
  Calendar,
  Layers,
  Edit3,
  Check,
  Search,
  BookOpen
} from 'lucide-react';
import type { SavedPaper } from '../types';
import { ApiService } from '../services/api';

interface SavedPapersDrawerProps {
  savedPapers: SavedPaper[];
  onRemovePaper: (paperId: string) => void;
  onViewDetails: (paperId: string) => void;
  onRefresh: () => void;
}

export const SavedPapersDrawer: React.FC<SavedPapersDrawerProps> = ({
  savedPapers,
  onRemovePaper,
  onViewDetails,
  onRefresh
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');

  const filteredPapers = savedPapers.filter(
    (p) =>
      p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.primary_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.notes && p.notes.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleStartEditNote = (paper: SavedPaper) => {
    setEditingNoteId(paper.paper_id);
    setNoteText(paper.notes || '');
  };

  const handleSaveNote = async (paperId: string) => {
    try {
      await ApiService.savePaper(paperId, noteText);
      setEditingNoteId(null);
      onRefresh();
    } catch (err) {
      console.error('Failed to update note:', err);
    }
  };

  const handleExportBibtex = () => {
    if (savedPapers.length === 0) return;
    const bibtexEntries = savedPapers.map((p, idx) => {
      const citeKey = `paper_${p.publication_year}_${idx + 1}`;
      const authorsFormatted = p.authors.join(' and ');
      return `@article{${citeKey},\n  title={${p.title}},\n  author={${authorsFormatted}},\n  year={${p.publication_year}},\n  journal={${p.venue}}\n}`;
    });

    const blob = new Blob([bibtexEntries.join('\n\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'research_finder_library.bib';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="saved-view-container">
      {/* Top Banner */}
      <div className="saved-hero-banner">
        <div className="hero-badge">
          <Bookmark className="badge-icon" />
          <span>Personal Research Library</span>
        </div>
        <div className="banner-flex-row">
          <div>
            <h1 className="hero-title">Saved Papers & Bookmarks</h1>
            <p className="hero-desc">
              Organize, annotate, and export your curated collection of research publications.
            </p>
          </div>
          {savedPapers.length > 0 && (
            <button type="button" className="export-bibtex-btn" onClick={handleExportBibtex}>
              <Download className="btn-icon" />
              <span>Export BibTeX</span>
            </button>
          )}
        </div>
      </div>

      {/* Search Filter Bar */}
      {savedPapers.length > 0 && (
        <div className="saved-filter-bar">
          <div className="saved-search-box">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Filter saved papers by title, category, or researcher notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="saved-search-input"
            />
          </div>
          <span className="saved-count-tag">
            {filteredPapers.length} of {savedPapers.length} Saved
          </span>
        </div>
      )}

      {/* List */}
      {savedPapers.length === 0 ? (
        <div className="empty-saved-state">
          <div className="empty-icon-wrapper">
            <Bookmark className="empty-icon" />
          </div>
          <h3>Your Library is Empty</h3>
          <p>
            Bookmark papers from search results to organize your research literature, attach notes, and export BibTeX citations.
          </p>
        </div>
      ) : filteredPapers.length === 0 ? (
        <div className="empty-saved-state">
          <p>No saved papers matching "{searchTerm}".</p>
        </div>
      ) : (
        <div className="saved-papers-grid">
          {filteredPapers.map((p) => (
            <div key={p.paper_id} className="saved-paper-card">
              <div className="saved-card-top">
                <span className="category-pill">{p.primary_category}</span>
                <span className="meta-item">
                  <Calendar className="meta-icon" /> {p.publication_year}
                </span>
                <span className="meta-item venue-pill">
                  <Layers className="meta-icon" /> {p.venue}
                </span>
              </div>

              <h3 className="saved-title" onClick={() => onViewDetails(p.paper_id)}>
                {p.title}
              </h3>

              <p className="saved-authors">
                {p.authors.join(', ')}
              </p>

              {/* Note Annotation Box */}
              <div className="saved-note-section">
                {editingNoteId === p.paper_id ? (
                  <div className="note-editor">
                    <textarea
                      className="note-textarea"
                      placeholder="Add research notes or observations on this paper..."
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      rows={2}
                    ></textarea>
                    <div className="note-editor-actions">
                      <button
                        type="button"
                        className="save-note-btn"
                        onClick={() => handleSaveNote(p.paper_id)}
                      >
                        <Check className="btn-icon" /> Save Note
                      </button>
                      <button
                        type="button"
                        className="cancel-note-btn"
                        onClick={() => setEditingNoteId(null)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="note-display" onClick={() => handleStartEditNote(p)}>
                    <Edit3 className="note-icon" />
                    <span className="note-text">
                      {p.notes ? p.notes : 'Click to add research notes...'}
                    </span>
                  </div>
                )}
              </div>

              {/* Card Footer */}
              <div className="saved-card-footer">
                <button
                  type="button"
                  className="view-details-btn"
                  onClick={() => onViewDetails(p.paper_id)}
                >
                  <BookOpen className="btn-icon" />
                  <span>Inspect Paper</span>
                </button>

                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => onRemovePaper(p.paper_id)}
                  title="Remove from saved papers"
                >
                  <Trash2 className="btn-icon" />
                  <span>Remove</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
