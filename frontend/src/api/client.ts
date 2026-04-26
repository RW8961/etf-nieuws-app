import type { HoldingsResponse } from "../types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchHoldings(forceRefresh = false): Promise<HoldingsResponse> {
  const url = `${BASE}${forceRefresh ? "/api/holdings?force_refresh=true" : "/api/holdings"}`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `API error: ${res.status}`);
  }
  return res.json();
}
