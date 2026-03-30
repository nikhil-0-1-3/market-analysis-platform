"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type SignalCard = {
  symbol: string;
  what_happened: string;
  may_move: string;
  direction: "buy_bias" | "sell_bias" | "watch";
  confidence_score: number;
  risk_warning: string;
  horizon: "intraday" | "swing";
  audit_id: string;
};

type LiveSignalsResponse = {
  region: string;
  generated_at: string;
  signals: SignalCard[];
};

type SourceEvent = {
  source: "news" | "social" | "market";
  headline: string;
  body: string;
  symbols: string[];
  sectors: string[];
  region: string;
  occurred_at?: string;
};

type ConnectorStatus = {
  cached_events: number;
  last_refresh_at: string | null;
  last_error: string | null;
  news_sources: number;
  social_sources: number;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

function directionLabel(direction: SignalCard["direction"]): string {
  if (direction === "buy_bias") return "Buy Bias";
  if (direction === "sell_bias") return "Sell Bias";
  return "Watch";
}

export default function SignalWorkbench() {
  const [region, setRegion] = useState("IN");
  const [headline, setHeadline] = useState("RBI commentary supports banking liquidity outlook");
  const [symbol, setSymbol] = useState("NSE:HDFCBANK");
  const [volumeSpike, setVolumeSpike] = useState("2.2");
  const [volatility, setVolatility] = useState("1.5");
  const [trendScore, setTrendScore] = useState("0.55");
  const [watchlistInput, setWatchlistInput] = useState("NSE:INFY, NSE:TCS, NSE:HDFCBANK");

  const [liveSignals, setLiveSignals] = useState<SignalCard[]>([]);
  const [liveEvents, setLiveEvents] = useState<SourceEvent[]>([]);
  const [connectorStatus, setConnectorStatus] = useState<ConnectorStatus | null>(null);
  const [generatedSignal, setGeneratedSignal] = useState<SignalCard | null>(null);
  const [batchSignals, setBatchSignals] = useState<SignalCard[]>([]);
  const [error, setError] = useState("");
  const [loadingLive, setLoadingLive] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadAutonomousData = async (refreshRemote = false) => {
    setLoadingLive(true);
    setError("");
    try {
      if (refreshRemote) {
        await fetch(`${API_BASE}/api/v1/intelligence/connectors/refresh-live?limit_per_source=20`, { method: "POST" });
      }

      const [statusRes, eventsRes, signalsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/intelligence/connectors/status`),
        fetch(`${API_BASE}/api/v1/intelligence/connectors/live-events?limit=30&region=${encodeURIComponent(region)}`),
        fetch(`${API_BASE}/api/v1/intelligence/live-signals?region=${encodeURIComponent(region)}`),
      ]);

      if (!statusRes.ok || !eventsRes.ok || !signalsRes.ok) {
        throw new Error("Live connector fetch failed");
      }

      const statusData: ConnectorStatus = await statusRes.json();
      const eventData: SourceEvent[] = await eventsRes.json();
      const signalData: LiveSignalsResponse = await signalsRes.json();

      setConnectorStatus(statusData);
      setLiveEvents(eventData);
      setLiveSignals(signalData.signals);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load live connector data");
    } finally {
      setLoadingLive(false);
    }
  };

  useEffect(() => {
    loadAutonomousData(false);
    const timer = window.setInterval(() => {
      loadAutonomousData(true);
    }, 120000);

    return () => window.clearInterval(timer);
  }, [region]);

  const summary = useMemo(() => {
    const cards = [generatedSignal, ...batchSignals, ...liveSignals].filter(Boolean) as SignalCard[];
    if (!cards.length) return { avg: 0, high: 0, count: 0 };
    const avg = cards.reduce((acc, c) => acc + c.confidence_score, 0) / cards.length;
    const high = Math.max(...cards.map((c) => c.confidence_score));
    return { avg, high, count: cards.length };
  }, [generatedSignal, batchSignals, liveSignals]);

  const onGenerate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    const payload = {
      event: {
        source: "news",
        headline,
        body: "Operator-generated event from dashboard workbench.",
        symbols: [symbol],
        sectors: ["Banking"],
        region,
      },
      price_action: {
        symbol,
        volume_spike: Number(volumeSpike),
        volatility: Number(volatility),
        trend_score: Number(trendScore),
      },
    };

    try {
      const res = await fetch(`${API_BASE}/api/v1/intelligence/generate-signal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Signal generation failed (${res.status})`);
      const data: SignalCard = await res.json();
      setGeneratedSignal(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate signal");
    } finally {
      setSubmitting(false);
    }
  };

  const onLoadBatchData = async () => {
    setError("");
    setSubmitting(true);
    try {
      const sourceRes = await fetch(`${API_BASE}/api/v1/intelligence/connectors/live-events?limit=12&region=${encodeURIComponent(region)}`);
      if (!sourceRes.ok) throw new Error(`Live connector failed (${sourceRes.status})`);
      const events: SourceEvent[] = await sourceRes.json();

      const batchRes = await fetch(`${API_BASE}/api/v1/intelligence/ingest-batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events }),
      });
      if (!batchRes.ok) throw new Error(`Batch ingest failed (${batchRes.status})`);
      const data = await batchRes.json();
      setBatchSignals(data.signals ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to run batch ingest");
    } finally {
      setSubmitting(false);
    }
  };

  const onScanWatchlist = async () => {
    setError("");
    setSubmitting(true);
    try {
      const symbols = watchlistInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const res = await fetch(`${API_BASE}/api/v1/intelligence/scan-watchlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbols, region, source: "market" }),
      });
      if (!res.ok) throw new Error(`Watchlist scan failed (${res.status})`);
      const data = await res.json();
      setBatchSignals(data.signals ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to scan watchlist");
    } finally {
      setSubmitting(false);
    }
  };

  const allCards = [generatedSignal, ...batchSignals, ...liveSignals].filter(Boolean) as SignalCard[];

  return (
    <section className="workbench">
      <div className="surface stats">
        <p className="kicker">Autonomous Feed</p>
        <h3>Live Decision Console</h3>
        <div className="metric-grid">
          <div><p>Average Confidence</p><strong>{summary.avg.toFixed(2)}</strong></div>
          <div><p>Highest Confidence</p><strong>{summary.high.toFixed(2)}</strong></div>
          <div><p>Total Signals</p><strong>{summary.count}</strong></div>
        </div>
        <div className="metric-grid">
          <div><p>Cached Events</p><strong>{connectorStatus?.cached_events ?? 0}</strong></div>
          <div><p>News Sources</p><strong>{connectorStatus?.news_sources ?? 0}</strong></div>
          <div><p>Social Sources</p><strong>{connectorStatus?.social_sources ?? 0}</strong></div>
        </div>
        <div className="button-row">
          <button type="button" disabled={submitting || loadingLive} onClick={() => loadAutonomousData(true)}>Refresh Live Sources</button>
        </div>
      </div>

      <section className="surface form">
        <p className="kicker">Live News + Social Trend Intake</p>
        <div className="event-list">
          {liveEvents.slice(0, 12).map((eventItem, idx) => (
            <article key={`${eventItem.headline}-${idx}`} className="event-row">
              <p><strong>{eventItem.source.toUpperCase()}</strong> · {eventItem.region}</p>
              <p>{eventItem.headline}</p>
              <p className="event-meta">{eventItem.symbols.join(", ")}</p>
            </article>
          ))}
        </div>
      </section>

      <form className="surface form" onSubmit={onGenerate}>
        <p className="kicker">Generate Signal</p>
        <div className="field-grid">
          <label>Region<input suppressHydrationWarning value={region} onChange={(e) => setRegion(e.target.value.toUpperCase())} maxLength={8} /></label>
          <label>Symbol<input suppressHydrationWarning value={symbol} onChange={(e) => setSymbol(e.target.value)} /></label>
          <label className="wide">Headline<input suppressHydrationWarning value={headline} onChange={(e) => setHeadline(e.target.value)} /></label>
          <label>Volume Spike<input suppressHydrationWarning value={volumeSpike} onChange={(e) => setVolumeSpike(e.target.value)} /></label>
          <label>Volatility<input suppressHydrationWarning value={volatility} onChange={(e) => setVolatility(e.target.value)} /></label>
          <label>Trend Score<input suppressHydrationWarning value={trendScore} onChange={(e) => setTrendScore(e.target.value)} /></label>
        </div>
        <div className="button-row">
          <button suppressHydrationWarning type="submit" disabled={submitting}>{submitting ? "Working..." : "Generate Explainable Signal"}</button>
          <button suppressHydrationWarning type="button" disabled={submitting} onClick={onLoadBatchData}>Batch From Live Feed</button>
        </div>
      </form>

      <section className="surface form">
        <p className="kicker">Watchlist Scanner</p>
        <label className="wide">
          Symbols (comma-separated)
          <input suppressHydrationWarning value={watchlistInput} onChange={(e) => setWatchlistInput(e.target.value)} />
        </label>
        <div className="button-row">
          <button suppressHydrationWarning type="button" disabled={submitting} onClick={onScanWatchlist}>Scan Watchlist</button>
        </div>
      </section>

      {error ? <div className="surface error">{error}</div> : null}
      {loadingLive ? <div className="surface">Loading live signals...</div> : null}

      <div className="cards">
        {allCards.map((signal) => (
          <article className="surface signal-card" key={signal.audit_id}>
            <p className="kicker">{signal.horizon.toUpperCase()} Signal</p>
            <h4>{signal.symbol}</h4>
            <p>{signal.what_happened}</p>
            <p><strong>Move:</strong> {signal.may_move}</p>
            <p><strong>Direction:</strong> {directionLabel(signal.direction)}</p>
            <p><strong>Confidence:</strong> {signal.confidence_score.toFixed(2)}</p>
            <p><strong>Risk:</strong> {signal.risk_warning}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
