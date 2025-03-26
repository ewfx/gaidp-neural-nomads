import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import TransactionsTable from "@/Chatbot/public/elements/TransactionsTable";

describe("TransactionsTable Component", () => {
  it("renders the component and displays transactions", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            transactions: [
              { id: "1", date: "2023-10-01", executerId: "E1", amount: 100 },
            ],
          }),
      })
    );

    render(<TransactionsTable />);

    expect(
      await screen.findByText("Unaudited Transactions")
    ).toBeInTheDocument();
    expect(await screen.findByText("1")).toBeInTheDocument();
    expect(await screen.findByText("E1")).toBeInTheDocument();
  });

  it("filters transactions by search term", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            transactions: [
              { id: "1", date: "2023-10-01", executerId: "E1", amount: 100 },
            ],
          }),
      })
    );

    render(<TransactionsTable />);

    const searchInput = await screen.findByPlaceholderText(
      "Search transactions..."
    );
    fireEvent.change(searchInput, { target: { value: "E1" } });

    expect(await screen.findByText("E1")).toBeInTheDocument();
  });

  it("handles audit button click", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            transactions: [
              { id: "1", date: "2023-10-01", executerId: "E1", amount: 100 },
            ],
          }),
      })
    );

    render(<TransactionsTable />);

    const auditButton = await screen.findByText("Audit");
    fireEvent.click(auditButton);

    expect(
      await screen.findByText("Auditing Transaction: 1")
    ).toBeInTheDocument();
  });
});
