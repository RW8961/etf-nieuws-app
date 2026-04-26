export interface NewsArticle {
  title: string;
  description: string | null;
  url: string;
  published_at: string;
  source_name: string;
}

export interface AggregatedCompany {
  ticker: string;
  company_name: string;
  weight_pct: number;
  etf_sources: string[];
  news: NewsArticle[];
}

export interface HoldingsResponse {
  etfs: string[];
  generated_at: string;
  companies: AggregatedCompany[];
}
