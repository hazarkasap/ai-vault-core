import React from "react";
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { Dashboard } from "./Dashboard.jsx";

afterEach(cleanup);
test("renders an accurate synthetic workflow summary", async () => {
  global.fetch = vi.fn().mockResolvedValue({ok: true, json: async () => ({
    iteration_status: "completed", event_count: 10, pending_approvals: 0,
    verification: "passed", goal: "Synthetic goal"
  })});
  render(<Dashboard />);
  expect(await screen.findByText("Synthetic goal")).toBeTruthy();
  expect(screen.getByText(/No autonomous model provider/)).toBeTruthy();
});

