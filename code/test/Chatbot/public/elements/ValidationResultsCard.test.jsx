import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ValidationResultsCard from "@/Chatbot/public/elements/ValidationResultsCard";

describe("ValidationResultsCard Component", () => {
  const mockResults = {
    total_rules: 10,
    total_transactions: 100,
    failed_transactions: 5,
    failure_rate: 5,
    execution_time: 2.5,
    timestamp: "2023-10-01T12:00:00Z",
    rule_performance: [
      {
        rule_id: "1",
        rule_name: "Rule 1",
        failures: 2,
        failure_rate: 2,
        execution_time: 0.5,
      },
    ],
    universal_failure_rules: [
      {
        rule_id: "2",
        rule_name: "Rule 2",
        sql_query: "SELECT * FROM transactions WHERE ...",
      },
    ],
  };

  it("renders the component and displays summary", () => {
    render(<ValidationResultsCard results={mockResults} />);

    expect(screen.getByText("Data Validation Results")).toBeInTheDocument();
    expect(screen.getByText("Total Rules: 10")).toBeInTheDocument();
    expect(screen.getByText("Failed Transactions: 5")).toBeInTheDocument();
  });

  it("switches to rule performance tab", () => {
    render(<ValidationResultsCard results={mockResults} />);

    const rulePerformanceTab = screen.getByText("Rule Performance");
    fireEvent.click(rulePerformanceTab);

    expect(screen.getByText("Rule ID")).toBeInTheDocument();
    expect(screen.getByText("Rule 1")).toBeInTheDocument();
  });

  it("switches to universal failures tab", () => {
    render(<ValidationResultsCard results={mockResults} />);

    const universalFailuresTab = screen.getByText("Universal Failures");
    fireEvent.click(universalFailuresTab);

    expect(screen.getByText("Rule 2")).toBeInTheDocument();
    expect(
      screen.getByText("SELECT * FROM transactions WHERE ...")
    ).toBeInTheDocument();
  });

  it("handles download button click", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        blob: () => Promise.resolve(new Blob(["mock data"])),
      })
    );

    render(<ValidationResultsCard results={mockResults} />);

    const downloadButton = screen.getByText("Download Results");
    fireEvent.click(downloadButton);

    expect(global.fetch).toHaveBeenCalled();
  });
});
