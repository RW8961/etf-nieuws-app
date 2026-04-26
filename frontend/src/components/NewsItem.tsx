import type { NewsArticle } from "../types";

interface Props {
  article: NewsArticle;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("nl-NL", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function NewsItem({ article }: Props) {
  return (
    <div style={{
      padding: "0.6rem 0",
      borderBottom: "1px solid #f0f0f0",
    }}>
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          fontWeight: 500,
          color: "#0070f3",
          textDecoration: "none",
          fontSize: "0.9rem",
          lineHeight: 1.4,
        }}
      >
        {article.title}
      </a>
      {article.description && (
        <p style={{ margin: "0.25rem 0 0", fontSize: "0.8rem", color: "#555" }}>
          {article.description}
        </p>
      )}
      <span style={{ fontSize: "0.75rem", color: "#999" }}>
        {article.source_name} · {formatDate(article.published_at)}
      </span>
    </div>
  );
}
