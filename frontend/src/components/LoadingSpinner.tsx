export function LoadingSpinner() {
  return (
    <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
      <div style={{
        display: "inline-block",
        width: "2rem",
        height: "2rem",
        border: "3px solid #ddd",
        borderTopColor: "#0070f3",
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <p style={{ marginTop: "1rem" }}>Holdings en nieuws ophalen…</p>
    </div>
  );
}
