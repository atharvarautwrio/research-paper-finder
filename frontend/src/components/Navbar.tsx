import React from 'react';
import {
  Search,
  TrendingUp,
  Award,
  Bookmark,
  Sun,
  Moon,
  Database,
  BookOpen
} from 'lucide-react';
import type { SystemStats } from '../types';

interface NavbarProps {
  activeTab: 'search' | 'analytics' | 'benchmark' | 'saved';
  setActiveTab: (tab: 'search' | 'analytics' | 'benchmark' | 'saved') => void;
  savedCount: number;
  darkMode: boolean;
  toggleDarkMode: () => void;
  systemStats: SystemStats | null;
  onOpenStats: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  savedCount,
  darkMode,
  toggleDarkMode,
  systemStats,
  onOpenStats
}) => {
  return (
    <header className="header-nav">
      <div className="nav-container">
        {/* Logo & Brand */}
        <div className="brand" onClick={() => setActiveTab('search')}>
          <div className="brand-logo-icon">
            <BookOpen className="icon-main" />
            <div className="logo-spark"></div>
          </div>
          <div className="brand-text">
            <span className="brand-title">Research<span className="brand-accent">Finder</span></span>
            <span className="brand-badge">30,000+ Papers</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search className="tab-icon" />
            <span>Search & Retrieval</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <TrendingUp className="tab-icon" />
            <span>Trends & Intelligence</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'benchmark' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmark')}
          >
            <Award className="tab-icon" />
            <span>IR Benchmarks</span>
            <span className="pulse-indicator"></span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            <Bookmark className="tab-icon" />
            <span>Saved Library</span>
            {savedCount > 0 && <span className="saved-badge">{savedCount}</span>}
          </button>
        </nav>

        {/* Quick Actions & System Status */}
        <div className="nav-actions">
          {systemStats && (
            <button
              className="system-health-pill"
              onClick={onOpenStats}
              title="Click to view Index Diagnostics & Stats"
            >
              <Database className="health-icon" />
              <span>{systemStats.indexed_papers_count.toLocaleString()} Papers</span>
              <span className="status-dot green"></span>
            </button>
          )}

          <button
            className="theme-toggle-btn"
            onClick={toggleDarkMode}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? <Sun className="theme-icon" /> : <Moon className="theme-icon" />}
          </button>
        </div>
      </div>
    </header>
  );
};
