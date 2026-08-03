import React, { useEffect, useState } from "react";

export function Dashboard({ apiBase = "http://127.0.0.1:8765" }) {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch(`${apiBase}/api/overview`).then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    }).then(setOverview).catch(() => setError("Observer API is unavailable."));
  }, [apiBase]);
  if (error) return <main><h1>AI Vault Observer</h1><p role="alert">{error}</p></main>;
  if (!overview) return <main><h1>AI Vault Observer</h1><p>Loading synthetic workflow…</p></main>;
  return <main>
    <header><p className="eyebrow">Local educational showcase</p><h1>AI Vault Observer</h1></header>
    <section className="grid" aria-label="Workflow overview">
      <article><span>Status</span><strong>{overview.iteration_status}</strong></article>
      <article><span>Events</span><strong>{overview.event_count}</strong></article>
      <article><span>Approvals</span><strong>{overview.pending_approvals}</strong></article>
      <article><span>Verification</span><strong>{overview.verification}</strong></article>
    </section>
    <section className="panel"><h2>Current goal</h2><p>{overview.goal}</p></section>
    <section className="panel"><h2>Architecture boundary</h2><p>Human approval is required. No autonomous model provider is bundled.</p></section>
  </main>;
}
