import { useEffect, useState } from "react";
import { fetchHoldings } from "../api/client";
import type { HoldingsResponse } from "../types";
import { CompanyCard } from "./CompanyCard";
import { ErrorBanner } from "./ErrorBanner";
import { LoadingSpinner } from "./LoadingSpinner";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("nl-NL", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function ETFDashboard() {
  const [data, setData] = useState<HoldingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    fetchHoldings(forceRefresh)
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={{ maxWidth: "860px", margin: "0 auto", padding: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.5rem" }}>📰 ETF Nieuws</h1>
          <p style={{ margin: "0.25rem 0 0", color: "#666", fontSize: "0.9rem" }}>
            Top holdings van <strong>IWDA</strong> &amp; <strong>EMIM</strong>
          </p>
        </div>
        <button
          onClick={() => load(true)}
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "0.5rem",
            border: "1px solid #d1d5db",
            background: loading ? "#f3f4f6" : "white",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "0.875rem",
          }}
        >
          {loading ? "Laden…" : "🔄 Ververs"}
        </button>
      </div>

      {data && !loading && (
        <p style={{ fontSize: "0.8rem", color: "#aaa", marginBottom: "1rem" }}>
          Bijgewerkt op {formatDate(data.generated_at)} · {data.companies.length} bedrijven
          {data.companies.some((c) => c.etf_sources.length > 1) && " (sommige in beide ETFs)"}
        </p>
      )}

      {loading && <LoadingSpinner />}
      {error && <ErrorBanner message={error} onRetry={() => load()} />}

      {!loading && data && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {data.companies.map((company) => (
            <CompanyCard key={company.ticker} company={company} />
          ))}
        </div>
      )}
    </div>
  );
}
