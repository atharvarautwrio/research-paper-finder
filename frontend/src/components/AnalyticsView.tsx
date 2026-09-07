import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Award,
  BookOpen,
  Layers,
  Users,
  BarChart3,
  Flame,
  ArrowUpRight,
  Sparkles,
  Tag,
  Compass
} from 'lucide-react';
import type { AnalyticsOverview, TopicCluster, TrendItem } from '../types';
import { ApiService } from '../services/api';

interface AnalyticsViewProps {
  onSearchTopic: (query: string) => void;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ onSearchTopic }) => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [topics, setTopics] = useState<TopicCluster[]>([]);
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [ovData, topicsData, trendsData] = await Promise.all([
          ApiService.getOverview(),
          ApiService.getTopics(),
          ApiService.getTrends()
        ]);
        setOverview(ovData);
        setTopics(topicsData);
        setTrends(trendsData);
      } catch (err) {
        console.error('Failed to load analytics intelligence:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="analytics-loading-view">
        <div className="spinner large"></div>
        <p className="loading-text">Computing corpus intelligence, topic clusters & CAGR growth trajectories...</p>
      </div>
    );
  }

  return (
    <div className="analytics-view-container">
      {/* Top Banner */}
      <div className="analytics-hero-banner">
        <div className="hero-badge">
          <Sparkles className="badge-icon" />
          <span>Corpus Intelligence & Trend Radar</span>
        </div>
        <h1 className="hero-title">Academic Research Trends & Topic Intelligence</h1>
        <p className="hero-desc">
          Continuous temporal analytics across 30,000+ papers, discovering research trajectory momentum, unsupervised topic clusters, and scholarly distribution.
        </p>
      </div>

      {/* KPI Stats Grid */}
      {overview && (
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon-wrapper blue">
              <BookOpen className="kpi-icon" />
            </div>
            <div className="kpi-content">
              <span className="kpi-value">{overview.total_papers.toLocaleString()}</span>
              <span className="kpi-label">Indexed Research Papers</span>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon-wrapper purple">
              <Users className="kpi-icon" />
            </div>
            <div className="kpi-content">
              <span className="kpi-value">{overview.total_authors.toLocaleString()}</span>
              <span className="kpi-label">Unique Authors & Researchers</span>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon-wrapper emerald">
              <Layers className="kpi-icon" />
            </div>
            <div className="kpi-content">
              <span className="kpi-value">{overview.total_venues.toLocaleString()}</span>
              <span className="kpi-label">Conferences & Journals</span>
            </div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon-wrapper amber">
              <Award className="kpi-icon" />
            </div>
            <div className="kpi-content">
              <span className="kpi-value">{overview.avg_citations.toLocaleString()}</span>
              <span className="kpi-label">Avg Citations / Paper</span>
            </div>
          </div>
        </div>
      )}

      {/* Temporal Trend Trajectories (CAGR) */}
      <section className="analytics-section">
        <div className="section-header-row">
          <div>
            <h2 className="section-heading">
              <TrendingUp className="section-icon" /> Research Growth Trajectories & CAGR
            </h2>
            <p className="section-subtext">
              Compound Annual Growth Rate (CAGR) and publication trajectory across 2018–2025.
            </p>
          </div>
        </div>

        <div className="trends-grid">
          {trends.map((item, idx) => {
            const maxVal = Math.max(...item.trajectory, 1);
            return (
              <div
                key={idx}
                className="trend-card"
                onClick={() => onSearchTopic(item.topic)}
                title="Click to search papers in this trend topic"
              >
                <div className="trend-top">
                  <div className="trend-title-group">
                    <h4 className="trend-name">{item.topic}</h4>
                    <span className="trend-paper-count">{item.total_papers.toLocaleString()} papers</span>
                  </div>
                  <div className="trend-badge-group">
                    <span className={`status-pill ${item.status.toLowerCase()}`}>
                      {item.status === 'Emerging' && <Flame className="pill-icon" />}
                      {item.status}
                    </span>
                    <span className="cagr-badge">
                      <ArrowUpRight className="cagr-icon" /> +{item.cagr}% CAGR
                    </span>
                  </div>
                </div>

                {/* Sparkline Visualizer */}
                <div className="sparkline-container">
                  <div className="sparkline-bars">
                    {item.trajectory.map((val, vi) => {
                      const heightPct = Math.round((val / maxVal) * 100);
                      return (
                        <div key={vi} className="sparkline-col" title={`${item.years[vi]}: ${val} papers`}>
                          <div
                            className="sparkline-bar"
                            style={{ height: `${Math.max(heightPct, 8)}%` }}
                          ></div>
                          <span className="sparkline-year">{String(item.years[vi]).slice(-2)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Discovered Topic Clusters */}
      <section className="analytics-section">
        <div className="section-header-row">
          <div>
            <h2 className="section-heading">
              <Compass className="section-icon" /> Discovered Topic Clusters
            </h2>
            <p className="section-subtext">
              Unsupervised clustering on the 30,000-paper embedding space with TF-IDF keyword extraction.
            </p>
          </div>
        </div>

        <div className="topics-grid">
          {topics.map((topic) => (
            <div
              key={topic.topic_id}
              className="topic-card"
              onClick={() => onSearchTopic(topic.name)}
            >
              <div className="topic-header">
                <span className="topic-badge">Cluster #{topic.topic_id + 1}</span>
                <span className="topic-count">{topic.paper_count.toLocaleString()} Papers</span>
              </div>

              <h4 className="topic-name">{topic.name}</h4>

              {/* Keywords */}
              <div className="topic-keywords">
                {topic.top_terms.slice(0, 6).map((term, ti) => (
                  <span key={ti} className="topic-keyword-tag">
                    <Tag className="tag-tiny" /> {term}
                  </span>
                ))}
              </div>

              {/* Sample Papers Preview */}
              <div className="topic-samples">
                <span className="sample-label">Representative Publications:</span>
                <ul className="sample-list">
                  {topic.sample_titles.slice(0, 2).map((st, si) => (
                    <li key={si} className="sample-title-item">
                      • {st}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Domain Distribution Charts */}
      {overview && (
        <section className="analytics-section">
          <div className="section-header-row">
            <div>
              <h2 className="section-heading">
                <BarChart3 className="section-icon" /> Corpus Distribution & Demographics
              </h2>
              <p className="section-subtext">
                Breakdown by academic discipline, publication era, and top conferences.
              </p>
            </div>
          </div>

          <div className="distribution-grid">
            {/* Categories */}
            <div className="distribution-card">
              <h4 className="dist-title">Papers by Research Discipline</h4>
              <div className="dist-bars-list">
                {overview.papers_by_category.map((cat, idx) => (
                  <div
                    key={idx}
                    className="dist-bar-item"
                    onClick={() => onSearchTopic(cat.category)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="dist-bar-label-row">
                      <span className="dist-name">{cat.category}</span>
                      <span className="dist-val">
                        {cat.count.toLocaleString()} ({cat.percentage}%)
                      </span>
                    </div>
                    <div className="dist-bar-track">
                      <div
                        className="dist-bar-fill"
                        style={{ width: `${Math.min(cat.percentage * 3, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Publication Timeline */}
            <div className="distribution-card">
              <h4 className="dist-title">Yearly Publication Volume</h4>
              <div className="timeline-chart">
                {overview.papers_by_year.map((py, idx) => {
                  const maxYear = Math.max(...overview.papers_by_year.map((p) => p.count), 1);
                  const hPct = Math.round((py.count / maxYear) * 100);
                  return (
                    <div key={idx} className="timeline-col">
                      <span className="timeline-val">{py.count.toLocaleString()}</span>
                      <div className="timeline-bar-track">
                        <div
                          className="timeline-bar-fill"
                          style={{ height: `${Math.max(hPct, 12)}%` }}
                        ></div>
                      </div>
                      <span className="timeline-year">{py.year}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Top Venues */}
            <div className="distribution-card">
              <h4 className="dist-title">Top Publication Venues</h4>
              <div className="venues-cloud">
                {overview.top_venues.map((v, idx) => (
                  <div
                    key={idx}
                    className="venue-chip"
                    onClick={() => onSearchTopic(v.venue)}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="v-name">{v.venue}</span>
                    <span className="v-count">{v.count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Keywords Cloud */}
            <div className="distribution-card">
              <h4 className="dist-title">Trending Subject Keywords</h4>
              <div className="keywords-cloud">
                {overview.top_keywords.map((kw, idx) => (
                  <span
                    key={idx}
                    className="keyword-bubble"
                    onClick={() => onSearchTopic(kw.keyword)}
                  >
                    {kw.keyword} <small>({kw.count})</small>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
