import { useState } from "react";
import type { AggregatedCompany } from "../types";
import { Disclaimer } from "./Disclaimer";
import { NewsItem } from "./NewsItem";

interface Props {
  company: AggregatedCompany;
}

const ETF_COLORS: Record<string, string> = {
  IWDA: "#0070f3",
  EMIM: "#00a36c",
};

export function CompanyCard({ company }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{
      background: "white",
      border: "1px solid #e5e7eb",
      borderRadius: "0.75rem",
      padding: "1rem 1.25rem",
      boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
    }}>
      <div
        style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", cursor: "pointer" }}
        onClick={() => setExpanded((v) => !v)}
      >
        <div>
          <span style={{ fontWeight: 700, fontSize: "1rem" }}>{company.ticker}</span>
          <span style={{ marginLeft: "0.5rem", color: "#555", fontSize: "0.9rem" }}>
            {company.company_name}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          {company.etf_sources.map((etf) => (
            <span
              key={etf}
              style={{
                fontSize: "0.7rem",
                fontWeight: 600,
                padding: "0.15rem 0.45rem",
                borderRadius: "9999px",
                background: ETF_COLORS[etf] ?? "#888",
                color: "white",
              }}
            >
              {etf}
            </span>
          ))}
          <span style={{ fontSize: "0.85rem", color: "#888", marginLeft: "0.25rem" }}>
            {company.weight_pct.toFixed(2)}%
          </span>
          <span style={{ fontSize: "0.8rem", color: "#aaa" }}>{expanded ? "▲" : "▼"}</span>
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: "0.75rem" }}>
          {company.news.length === 0 ? (
            <p style={{ color: "#999", fontSize: "0.85rem" }}>Geen recent nieuws gevonden.</p>
          ) : (
            company.news.map((article, i) => (
              <NewsItem key={i} article={article} />
            ))
          )}
          <Disclaimer />
        </div>
      )}
    </div>
  );
}
