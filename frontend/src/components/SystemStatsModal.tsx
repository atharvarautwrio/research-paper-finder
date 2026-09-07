import React, { useState } from 'react';
import {
  X,
  Database,
  HardDrive,
  Clock,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import type { SystemStats } from '../types';
import { ApiService } from '../services/api';

interface SystemStatsModalProps {
  stats: SystemStats | null;
  onClose: () => void;
  onRefresh: () => void;
}

export const SystemStatsModal: React.FC<SystemStatsModalProps> = ({
  stats,
  onClose,
  onRefresh
}) => {
  const [reindexing, setReindexing] = useState(false);
  const [reindexMessage, setReindexMessage] = useState<string | null>(null);

  if (!stats) return null;

  const handleTriggerReindex = async () => {
    setReindexing(true);
    try {
      const res = await ApiService.triggerReindex();
      setReindexMessage(res.message);
      setTimeout(onRefresh, 3000);
    } catch (err) {
      console.error('Failed to trigger reindex:', err);
    } finally {
      setReindexing(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    if (mins >= 60) {
      const hrs = Math.floor(mins / 60);
      return `${hrs}h ${mins % 60}m`;
    }
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container stats-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-left">
            <div className="modal-icon-badge blue">
              <Database className="icon" />
            </div>
            <div>
              <h2 className="modal-title">System Diagnostics & Index Health</h2>
              <p className="modal-subtitle">Real-time Information Retrieval architecture telemetry</p>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X className="close-icon" />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body scrollable">
          {/* Status Header Pill */}
          <div className="stats-hero-banner">
            <div className="status-flex">
              <div className="status-indicator-group">
                <span className="status-circle green"></span>
                <span className="status-text">Engine Status: <strong>{stats.system_status}</strong></span>
              </div>
              <span className="uptime-tag">
                <Clock className="tag-icon" /> Uptime: {formatUptime(stats.uptime_seconds)}
              </span>
            </div>
          </div>

          {/* Core Metrics Grid */}
          <div className="stats-kpi-grid">
            <div className="stat-metric-card">
              <span className="s-label">Total Indexed Papers</span>
              <span className="s-val">{(stats?.indexed_papers_count || 30000).toLocaleString()}</span>
              <span className="s-sub">30,000 document target corpus</span>
            </div>

            <div className="stat-metric-card">
              <span className="s-label">Vocabulary Size</span>
              <span className="s-val">{stats.vocabulary_size.toLocaleString()} terms</span>
              <span className="s-sub">Inverted index unique stems</span>
            </div>

            <div className="stat-metric-card">
              <span className="s-label">Total Postings Entries</span>
              <span className="s-val">{stats.total_postings_count.toLocaleString()}</span>
              <span className="s-sub">Positional field inverted index</span>
            </div>

            <div className="stat-metric-card">
              <span className="s-label">Memory Footprint</span>
              <span className="s-val">{stats.memory_usage_mb} MB</span>
              <span className="s-sub">Resident process RAM</span>
            </div>

            <div className="stat-metric-card">
              <span className="s-label">Embedding Dimensions</span>
              <span className="s-val">{stats.embedding_dimension}-d</span>
              <span className="s-sub">Matrix: {stats.embeddings_matrix_shape.join(' × ')}</span>
            </div>

            <div className="stat-metric-card">
              <span className="s-label">Cache Hit Ratio</span>
              <span className="s-val">
                {stats.cache_stats.cache_hits + stats.cache_stats.cache_misses > 0
                  ? `${Math.round((stats.cache_stats.cache_hits / (stats.cache_stats.cache_hits + stats.cache_stats.cache_misses)) * 100)}%`
                  : '100%'}
              </span>
              <span className="s-sub">{stats.cache_stats.cache_hits} hits / {stats.cache_stats.cache_misses} misses</span>
            </div>
          </div>

          {/* Index Artifacts Integrity */}
          <div className="stats-section">
            <h3 className="section-title">
              <HardDrive className="section-icon" /> Index File Artifacts
            </h3>
            <div className="index-files-list">
              {Object.entries(stats.index_files).map(([fKey, fStatus]) => (
                <div key={fKey} className="index-file-row">
                  <div className="file-info">
                    <CheckCircle2 className="file-status-icon green" />
                    <span className="file-name">{fKey.replace(/_/g, ' ').toUpperCase()}</span>
                  </div>
                  <span className="file-status-tag">{fStatus}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Re-indexing Action */}
          <div className="stats-reindex-box">
            <div className="reindex-info">
              <h4>Rebuild & Reindex Corpus</h4>
              <p>Trigger background dataset generation and re-computation of all retrieval models.</p>
              {reindexMessage && <p className="reindex-alert">{reindexMessage}</p>}
            </div>
            <button
              type="button"
              className={`trigger-reindex-btn ${reindexing ? 'loading' : ''}`}
              onClick={handleTriggerReindex}
              disabled={reindexing}
            >
              <RefreshCw className={`btn-icon ${reindexing ? 'spin' : ''}`} />
              <span>{reindexing ? 'Triggering...' : 'Re-index Pipeline'}</span>
            </button>
          </div>
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
