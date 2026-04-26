import { ETFDashboard } from "./components/ETFDashboard";

export function App() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#f9fafb",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    }}>
      <ETFDashboard />
    </div>
  );
}
