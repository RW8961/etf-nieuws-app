interface Props {
  message: string;
  onRetry: () => void;
}

export function ErrorBanner({ message, onRetry }: Props) {
  return (
    <div style={{
      background: "#fff3f3",
      border: "1px solid #ffb3b3",
      borderRadius: "0.5rem",
      padding: "1rem 1.5rem",
      margin: "2rem auto",
      maxWidth: "600px",
    }}>
      <strong>Fout bij het laden:</strong> {message}
      <button
        onClick={onRetry}
        style={{
          marginLeft: "1rem",
          padding: "0.25rem 0.75rem",
          cursor: "pointer",
          borderRadius: "0.25rem",
          border: "1px solid #ccc",
          background: "white",
        }}
      >
        Opnieuw proberen
      </button>
    </div>
  );
}
