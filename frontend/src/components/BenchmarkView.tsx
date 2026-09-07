import React, { useState, useEffect } from 'react';
import {
  Award,
  Play,
  BarChart2,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Layers
} from 'lucide-react';
import type { BenchmarkReport } from '../types';
import { ApiService } from '../services/api';

export const BenchmarkView: React.FC = () => {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningBenchmark, setRunningBenchmark] = useState(false);
  const [expandedQuery, setExpandedQuery] = useState<number | null>(null);

  const fetchBenchmark = async (forceRerun = false) => {
    if (forceRerun) setRunningBenchmark(true);
    else setLoading(true);

    try {
      const data = await ApiService.getBenchmark(forceRerun);
      setReport(data);
    } catch (err) {
      console.error('Failed to run IR benchmark:', err);
    } finally {
      setLoading(false);
      setRunningBenchmark(false);
    }
  };

  useEffect(() => {
    fetchBenchmark();
  }, []);

  if (loading) {
    return (
      <div className="benchmark-loading-view">
        <div className="spinner large"></div>
        <p className="loading-text">Computing IR Evaluation Metrics (MAP, MRR, NDCG@10, P@10, Recall)...</p>
      </div>
    );
  }

  const hybridMetrics = report?.methods.find((m) => m.method_name.includes('Hybrid'));

  return (
    <div className="benchmark-view-container">
      {/* Hero Banner */}
      <div className="benchmark-hero-banner">
        <div className="hero-badge">
          <Award className="badge-icon" />
          <span>IR Evaluation & Benchmarking Suite</span>
        </div>
        <div className="banner-flex-row">
          <div>
            <h1 className="hero-title">Comparative Information Retrieval Evaluation</h1>
            <p className="hero-desc">
              Rigorous evaluation comparing Okapi BM25, TF-IDF Vector Space, Dense Semantic Embeddings, and Hybrid Ranking across standard Cranfield-style relevance judgments.
            </p>
          </div>
          <button
            type="button"
            className={`run-benchmark-btn ${runningBenchmark ? 'running' : ''}`}
            onClick={() => fetchBenchmark(true)}
            disabled={runningBenchmark}
          >
            {runningBenchmark ? (
              <>
                <span className="spinner"></span>
                <span>Evaluating Queries...</span>
              </>
            ) : (
              <>
                <Play className="btn-icon" />
                <span>Run Live Benchmark</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Primary KPI Metric Cards (Hybrid Ranker) */}
      {hybridMetrics && (
        <div className="benchmark-kpis-grid">
          <div className="b-kpi-card highlight">
            <div className="kpi-top">
              <span className="b-kpi-label">Mean Average Precision (MAP)</span>
              <span className="b-kpi-badge">Top Metric</span>
            </div>
            <span className="b-kpi-value">{hybridMetrics.map_score.toFixed(3)}</span>
            <span className="b-kpi-sub">Hybrid Ranker global AP</span>
          </div>

          <div className="b-kpi-card">
            <div className="kpi-top">
              <span className="b-kpi-label">NDCG @ 10</span>
              <span className="b-kpi-badge">Graded</span>
            </div>
            <span className="b-kpi-value">{hybridMetrics.ndcg_at_10.toFixed(3)}</span>
            <span className="b-kpi-sub">Normalized Discounted Gain</span>
          </div>

          <div className="b-kpi-card">
            <div className="kpi-top">
              <span className="b-kpi-label">Mean Reciprocal Rank (MRR)</span>
              <span className="b-kpi-badge">First Hit</span>
            </div>
            <span className="b-kpi-value">{hybridMetrics.mrr_score.toFixed(3)}</span>
            <span className="b-kpi-sub">Rank of 1st relevant document</span>
          </div>

          <div className="b-kpi-card">
            <div className="kpi-top">
              <span className="b-kpi-label">Precision @ 10</span>
              <span className="b-kpi-badge">Accuracy</span>
            </div>
            <span className="b-kpi-value">{(hybridMetrics.precision_at_10 * 100).toFixed(1)}%</span>
            <span className="b-kpi-sub">Relevant papers in top 10</span>
          </div>

          <div className="b-kpi-card">
            <div className="kpi-top">
              <span className="b-kpi-label">Recall @ 20</span>
              <span className="b-kpi-badge">Coverage</span>
            </div>
            <span className="b-kpi-value">{(hybridMetrics.recall_at_20 * 100).toFixed(1)}%</span>
            <span className="b-kpi-sub">Total relevant pool retrieved</span>
          </div>

          <div className="b-kpi-card">
            <div className="kpi-top">
              <span className="b-kpi-label">Avg Search Latency</span>
              <span className="b-kpi-badge">Speed</span>
            </div>
            <span className="b-kpi-value">{hybridMetrics.avg_latency_ms.toFixed(1)}ms</span>
            <span className="b-kpi-sub">Sub-50ms execution speed</span>
          </div>
        </div>
      )}

      {/* Summary Analysis Banner */}
      {report?.summary_analysis && (
        <div className="benchmark-summary-box">
          <div className="summary-icon-wrapper">
            <Sparkles className="summary-icon" />
          </div>
          <div>
            <h4 className="summary-heading">Benchmark Findings & Analysis</h4>
            <p className="summary-text">{report.summary_analysis}</p>
          </div>
        </div>
      )}

      {/* Method Comparison Table */}
      {report && (
        <section className="benchmark-section">
          <div className="section-header-row">
            <div>
              <h2 className="section-heading">
                <BarChart2 className="section-icon" /> Multi-Method Comparison Matrix
              </h2>
              <p className="section-subtext">
                Comprehensive empirical comparison across {report.num_queries} standardized query benchmark sets.
              </p>
            </div>
          </div>

          <div className="table-responsive-wrapper">
            <table className="benchmark-table">
              <thead>
                <tr>
                  <th>Retrieval Method</th>
                  <th>MAP</th>
                  <th>MRR</th>
                  <th>NDCG@10</th>
                  <th>NDCG@5</th>
                  <th>P@5</th>
                  <th>P@10</th>
                  <th>Recall@10</th>
                  <th>Recall@20</th>
                  <th>F1-Score</th>
                  <th>Avg Latency</th>
                </tr>
              </thead>
              <tbody>
                {report.methods.map((m, idx) => {
                  const isHybrid = m.method_name.includes('Hybrid');
                  return (
                    <tr key={idx} className={isHybrid ? 'highlight-row' : ''}>
                      <td className="method-name-cell">
                        <div className="method-label-group">
                          {isHybrid && <span className="winner-star">★</span>}
                          <span className="m-name">{m.method_name}</span>
                          {isHybrid && <span className="winner-pill">Best Overall</span>}
                        </div>
                      </td>
                      <td className="metric-cell bold">{m.map_score.toFixed(3)}</td>
                      <td className="metric-cell">{m.mrr_score.toFixed(3)}</td>
                      <td className="metric-cell bold">{m.ndcg_at_10.toFixed(3)}</td>
                      <td className="metric-cell">{m.ndcg_at_5.toFixed(3)}</td>
                      <td className="metric-cell">{(m.precision_at_5 * 100).toFixed(1)}%</td>
                      <td className="metric-cell">{(m.precision_at_10 * 100).toFixed(1)}%</td>
                      <td className="metric-cell">{(m.recall_at_10 * 100).toFixed(1)}%</td>
                      <td className="metric-cell">{(m.recall_at_20 * 100).toFixed(1)}%</td>
                      <td className="metric-cell">{m.f1_score.toFixed(3)}</td>
                      <td className="metric-cell latency-cell">
                        <Clock className="clock-icon" /> {m.avg_latency_ms.toFixed(1)} ms
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Per-Query Evaluation Accordion */}
      {report && report.query_details && (
        <section className="benchmark-section">
          <div className="section-header-row">
            <div>
              <h2 className="section-heading">
                <Layers className="section-icon" /> Query-Level Evaluation Breakdown
              </h2>
              <p className="section-subtext">
                Detailed metrics for individual benchmark queries across each retrieval model.
              </p>
            </div>
          </div>

          <div className="queries-accordion-list">
            {report.query_details.map((q, qIdx) => {
              const isOpen = expandedQuery === qIdx;
              return (
                <div key={qIdx} className={`query-acc-item ${isOpen ? 'open' : ''}`}>
                  <button
                    type="button"
                    className="query-acc-header"
                    onClick={() => setExpandedQuery(isOpen ? null : qIdx)}
                  >
                    <div className="q-left">
                      <span className="q-num">Q{qIdx + 1}</span>
                      <span className="q-title">"{q.query}"</span>
                      <span className="q-category">{q.category}</span>
                    </div>
                    <div className="q-right">
                      <span className="q-judgments">{q.num_judgments} Ground Truth Papers</span>
                      {isOpen ? <ChevronUp className="chevron" /> : <ChevronDown className="chevron" />}
                    </div>
                  </button>

                  {isOpen && (
                    <div className="query-acc-body">
                      <table className="mini-eval-table">
                        <thead>
                          <tr>
                            <th>Method</th>
                            <th>Precision @ 10</th>
                            <th>Average Precision (AP)</th>
                            <th>Reciprocal Rank (RR)</th>
                            <th>NDCG @ 10</th>
                            <th>Latency</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(q.methods).map(([mKey, mScores]) => (
                            <tr key={mKey} className={mKey === 'hybrid' ? 'hybrid-row' : ''}>
                              <td className="m-col">{mKey.toUpperCase()}</td>
                              <td>{(mScores['p@10'] * 100).toFixed(1)}%</td>
                              <td className="bold">{mScores.map.toFixed(3)}</td>
                              <td>{mScores.mrr.toFixed(3)}</td>
                              <td className="bold">{mScores['ndcg@10'].toFixed(3)}</td>
                              <td>{mScores.latency_ms} ms</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
};
