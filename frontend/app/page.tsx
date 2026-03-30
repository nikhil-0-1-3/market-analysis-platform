"use client";

import { useEffect, useMemo, useState } from "react";

type Timeframe = "1D" | "1W" | "1M" | "3M";
type SectorId = "Banking" | "IT" | "Infra" | "Energy" | "Pharma";
type SortBy = "performance" | "price" | "volume";

type StockRow = {
  symbol: string;
  name: string;
  price: number;
  changePct: number;
  volumeCr: number;
  series: number[];
};

type SectorBlock = {
  mood: string;
  note: string;
  series: Record<Timeframe, number[]>;
  stocks: StockRow[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

const sectorData: Record<SectorId, SectorBlock> = {
  Banking: {
    mood: "Happy",
    note: "Rate and liquidity tone remains supportive.",
    series: {
      "1D": [100, 101, 101.8, 102.5, 102.2, 103.1, 103.8, 104.2],
      "1W": [100, 100.4, 101.5, 102.1, 102.8, 103.4, 104.2, 104.9],
      "1M": [100, 99.5, 100.8, 101.7, 102.9, 103.3, 104.4, 105.6],
      "3M": [100, 98.8, 99.7, 101.1, 102.6, 104.1, 105.8, 107.2],
    },
    stocks: [
      { symbol: "HDFCBANK", name: "HDFC Bank", price: 1642, changePct: 1.2, volumeCr: 3850, series: [100, 101, 101.4, 102.6, 102.1, 103.4] },
      { symbol: "ICICIBANK", name: "ICICI Bank", price: 1188, changePct: 1.5, volumeCr: 3410, series: [100, 100.7, 101.1, 101.9, 102.2, 103.0] },
      { symbol: "AXISBANK", name: "Axis Bank", price: 1156, changePct: 0.9, volumeCr: 2010, series: [100, 100.2, 100.4, 101.2, 101.5, 102.0] },
    ],
  },
  IT: {
    mood: "Nervous",
    note: "Global demand commentary is mixed.",
    series: {
      "1D": [100, 99.8, 99.5, 99.7, 99.1, 98.8, 99.0, 98.7],
      "1W": [100, 99.4, 99.1, 98.7, 99.0, 98.5, 98.3, 98.1],
      "1M": [100, 99.8, 99.2, 98.7, 98.1, 97.8, 97.4, 97.0],
      "3M": [100, 101.2, 100.4, 99.8, 98.5, 97.2, 96.4, 95.8],
    },
    stocks: [
      { symbol: "INFY", name: "Infosys", price: 1487, changePct: -0.8, volumeCr: 1290, series: [100, 99.5, 99.1, 98.9, 98.4, 98.1] },
      { symbol: "TCS", name: "TCS", price: 4102, changePct: -0.5, volumeCr: 980, series: [100, 99.9, 99.6, 99.3, 99.0, 98.8] },
      { symbol: "WIPRO", name: "Wipro", price: 498, changePct: -1.1, volumeCr: 740, series: [100, 99.4, 99.2, 98.8, 98.2, 97.9] },
    ],
  },
  Infra: {
    mood: "Excited",
    note: "Project pipeline is broad and active.",
    series: {
      "1D": [100, 100.5, 101.1, 101.8, 102.4, 103.2, 103.6, 104.4],
      "1W": [100, 100.6, 101.7, 102.8, 103.4, 104.0, 104.8, 105.3],
      "1M": [100, 101.2, 102.4, 103.1, 104.3, 105.6, 106.4, 107.1],
      "3M": [100, 101.8, 103.5, 105.2, 106.7, 108.0, 109.4, 110.9],
    },
    stocks: [
      { symbol: "LT", name: "L&T", price: 3512, changePct: 2.1, volumeCr: 1890, series: [100, 101.4, 102.1, 103.8, 104.5, 106.2] },
      { symbol: "IRFC", name: "IRFC", price: 196, changePct: 1.7, volumeCr: 1310, series: [100, 100.7, 101.8, 102.9, 103.2, 104.8] },
      { symbol: "RVNL", name: "RVNL", price: 327, changePct: 2.4, volumeCr: 990, series: [100, 101.1, 102.7, 103.5, 104.1, 105.4] },
    ],
  },
  Energy: {
    mood: "Unsure",
    note: "Prices swing on global cues.",
    series: {
      "1D": [100, 100.1, 99.9, 100.4, 100.0, 100.6, 100.3, 100.8],
      "1W": [100, 100.6, 100.1, 99.8, 100.3, 100.7, 100.2, 100.5],
      "1M": [100, 101.1, 100.3, 99.6, 100.5, 99.8, 100.2, 100.7],
      "3M": [100, 99.4, 100.2, 101.5, 100.1, 99.6, 100.8, 101.3],
    },
    stocks: [
      { symbol: "RELIANCE", name: "Reliance", price: 2918, changePct: 0.4, volumeCr: 2740, series: [100, 100.6, 100.1, 100.8, 101.2, 101.4] },
      { symbol: "ONGC", name: "ONGC", price: 286, changePct: -0.2, volumeCr: 860, series: [100, 100.4, 99.8, 99.7, 100.1, 100.0] },
      { symbol: "IOC", name: "IOC", price: 183, changePct: 0.3, volumeCr: 710, series: [100, 99.9, 100.2, 100.4, 100.1, 100.5] },
    ],
  },
  Pharma: {
    mood: "Steady",
    note: "Defensive buying continues.",
    series: {
      "1D": [100, 100.3, 100.7, 100.5, 100.9, 101.2, 101.0, 101.4],
      "1W": [100, 100.4, 100.9, 101.5, 101.7, 102.0, 101.8, 102.2],
      "1M": [100, 100.8, 101.6, 102.1, 102.5, 103.1, 103.4, 103.9],
      "3M": [100, 101.0, 102.2, 103.8, 104.4, 105.1, 105.8, 106.4],
    },
    stocks: [
      { symbol: "SUNPHARMA", name: "Sun Pharma", price: 1748, changePct: 0.9, volumeCr: 930, series: [100, 100.6, 101.1, 101.7, 102.0, 102.6] },
      { symbol: "CIPLA", name: "Cipla", price: 1492, changePct: 0.6, volumeCr: 790, series: [100, 100.4, 100.8, 101.2, 101.4, 101.9] },
      { symbol: "DRREDDY", name: "Dr Reddy", price: 6892, changePct: 0.5, volumeCr: 620, series: [100, 100.3, 100.9, 101.3, 101.6, 102.0] },
    ],
  },
};

function linePath(series: number[], width: number, height: number): string {
  const min = Math.min(...series);
  const max = Math.max(...series);
  const range = max - min || 1;
  return series
    .map((v, i) => {
      const x = (i / (series.length - 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

function sparkPath(series: number[]): string {
  return linePath(series, 120, 28);
}

export default function HomePage() {
  const [sector, setSector] = useState<SectorId>("Banking");
  const [timeframe, setTimeframe] = useState<Timeframe>("1W");
  const [sortBy, setSortBy] = useState<SortBy>("performance");
  const [search, setSearch] = useState("");
  const [selectedStock, setSelectedStock] = useState<string>(sectorData.Banking.stocks[0].symbol);
  const [liveState, setLiveState] = useState("updated just now");

  useEffect(() => {
    setSelectedStock(sectorData[sector].stocks[0].symbol);
  }, [sector]);

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/intelligence/connectors/status`);
        if (!res.ok) return;
        const data = await res.json();
        if (!alive) return;
        setLiveState(data.last_refresh_at ? "live" : "using local model");
      } catch {
        if (alive) setLiveState("using local model");
      }
    };
    poll();
    const t = setInterval(poll, 60000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const current = sectorData[sector];
  const series = current.series[timeframe];
  const netChange = (((series[series.length - 1] - series[0]) / series[0]) * 100).toFixed(2);
  const chartColor = Number(netChange) >= 0 ? "var(--color-text-success)" : "var(--color-text-danger)";

  const stockRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    const rows = current.stocks.filter((s) =>
      `${s.name} ${s.symbol}`.toLowerCase().includes(query),
    );

    const sorted = [...rows].sort((a, b) => {
      if (sortBy === "price") return b.price - a.price;
      if (sortBy === "volume") return b.volumeCr - a.volumeCr;
      return b.changePct - a.changePct;
    });
    return sorted;
  }, [current.stocks, search, sortBy]);

  const focused = stockRows.find((s) => s.symbol === selectedStock) ?? stockRows[0];

  return (
    <>
      <div className="topbar">
        <div className="brand">market<em>sense</em></div>
        <div className="live-row">
          <div className="dot"></div>
          <span className="live-txt">Watching markets live · {liveState}</span>
        </div>
      </div>

      <div className="greeting">
        <div className="avatar">👋</div>
        <div>
          <div className="greet-title">Control your market view in real time.</div>
          <div className="greet-sub">Pick a sector, switch timeframe, sort stocks, and read growth/loss with a clear chart. Everything below is interactive.</div>
        </div>
      </div>

      <section className="panel controls-panel">
        <div className="section-head" style={{ marginTop: 0 }}>Sector Controls</div>
        <div className="control-grid">
          <div>
            <p className="control-label">Sector</p>
            <div className="chip-row">
              {(Object.keys(sectorData) as SectorId[]).map((key) => (
                <button key={key} type="button" className={`control-chip ${sector === key ? "active" : ""}`} onClick={() => setSector(key)}>{key}</button>
              ))}
            </div>
          </div>
          <div>
            <p className="control-label">Timeframe</p>
            <div className="chip-row">
              {(["1D", "1W", "1M", "3M"] as Timeframe[]).map((tf) => (
                <button key={tf} type="button" className={`control-chip ${timeframe === tf ? "active" : ""}`} onClick={() => setTimeframe(tf)}>{tf}</button>
              ))}
            </div>
          </div>
          <div>
            <p className="control-label">Sort Stocks</p>
            <div className="chip-row">
              {([
                ["performance", "Performance"],
                ["price", "Price"],
                ["volume", "Volume"],
              ] as [SortBy, string][]).map(([v, label]) => (
                <button key={v} type="button" className={`control-chip ${sortBy === v ? "active" : ""}`} onClick={() => setSortBy(v)}>{label}</button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="panel chart-panel">
        <div className="chart-head">
          <div>
            <div className="section-head" style={{ marginTop: 0 }}>{sector} Sector Growth/Loss</div>
            <p className="chart-sub">Mood: {current.mood} · {current.note}</p>
          </div>
          <div className={`chart-badge ${Number(netChange) >= 0 ? "up" : "dn"}`}>
            {Number(netChange) >= 0 ? "+" : ""}{netChange}% ({timeframe})
          </div>
        </div>
        <svg viewBox="0 0 720 220" className="main-chart" role="img" aria-label={`${sector} growth chart`}>
          <path d={linePath(series, 720, 220)} fill="none" stroke={chartColor} strokeWidth="3" strokeLinecap="round" />
        </svg>
      </section>

      <div className="two-col">
        <section className="panel">
          <div className="section-head" style={{ marginTop: 0 }}>Stocks in {sector}</div>
          <input className="stock-search" placeholder="Search stock by name or symbol" value={search} onChange={(e) => setSearch(e.target.value)} />
          <div className="stock-grid">
            {stockRows.map((row) => (
              <button key={row.symbol} type="button" className={`stock-card ${selectedStock === row.symbol ? "selected" : ""}`} onClick={() => setSelectedStock(row.symbol)}>
                <div className="stock-top">
                  <div>
                    <p className="stock-name">{row.name}</p>
                    <p className="stock-symbol">{row.symbol}</p>
                  </div>
                  <div className="stock-price">₹{row.price.toLocaleString("en-IN")}</div>
                </div>
                <div className="stock-mid">
                  <span className={row.changePct >= 0 ? "up" : "dn"}>{row.changePct >= 0 ? "+" : ""}{row.changePct.toFixed(2)}%</span>
                  <span className="stock-vol">Vol {row.volumeCr.toLocaleString("en-IN")} Cr</span>
                </div>
                <svg viewBox="0 0 120 28" className="spark">
                  <path d={sparkPath(row.series)} fill="none" stroke={row.changePct >= 0 ? "var(--color-text-success)" : "var(--color-text-danger)"} strokeWidth="2" />
                </svg>
              </button>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="section-head" style={{ marginTop: 0 }}>Focused Stock</div>
          {focused ? (
            <>
              <h3 className="focus-title">{focused.name} ({focused.symbol})</h3>
              <p className="focus-meta">Latest: ₹{focused.price.toLocaleString("en-IN")} · Volume: {focused.volumeCr.toLocaleString("en-IN")} Cr</p>
              <p className={`focus-change ${focused.changePct >= 0 ? "up" : "dn"}`}>{focused.changePct >= 0 ? "+" : ""}{focused.changePct.toFixed(2)}% today</p>
              <svg viewBox="0 0 360 120" className="focus-chart">
                <path d={linePath(focused.series, 360, 120)} fill="none" stroke={focused.changePct >= 0 ? "var(--color-text-success)" : "var(--color-text-danger)"} strokeWidth="3" strokeLinecap="round" />
              </svg>
              <div className="ask-row" style={{ marginTop: 12 }}>
                <div className="ask-label">Quick actions:</div>
                <div className="ask-chips">
                  <button className="ask-chip" type="button">Add to Watchlist</button>
                  <button className="ask-chip" type="button">Set Alert ±2%</button>
                  <button className="ask-chip" type="button">Compare with Sector</button>
                  <button className="ask-chip" type="button">Show Risk Notes</button>
                </div>
              </div>
            </>
          ) : (
            <p className="greet-sub">No stock available for this filter.</p>
          )}
        </section>
      </div>

      <footer>marketsense · interactive market UX build</footer>
    </>
  );
}
