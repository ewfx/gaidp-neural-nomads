import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RulesTableNonEditable from "../../../../Chatbot/public/elements/RulesTableNonEditable";

describe("RulesTableNonEditable Component", () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            rules: [
              {
                id: 1,
                name: "Rule 1",
                description: "Description 1",
                status: "Active",
              },
              {
                id: 2,
                name: "Rule 2",
                description: "Description 2",
                status: "Inactive",
              },
              {
                id: 3,
                name: "Rule 3",
                description: "Description 3",
                status: "Active",
              },
              {
                id: 4,
                name: "Rule 4",
                description: "Description 4",
                status: "Inactive",
              },
              {
                id: 5,
                name: "Rule 5",
                description: "Description 5",
                status: "Active",
              },
              {
                id: 6,
                name: "Rule 6",
                description: "Description 6",
                status: "Inactive",
              },
            ],
          }),
      })
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test("renders the component and fetches rules", async () => {
    render(<RulesTableNonEditable />);
    expect(screen.getByText(/Rules Table/i)).toBeInTheDocument();
    await waitFor(() =>
      expect(global.fetch).toHaveBeenCalledWith("http://localhost:5000/dbget")
    );
    expect(screen.getByText("Rule 1")).toBeInTheDocument();
  });

  test("filters rules based on search input", async () => {
    render(<RulesTableNonEditable />);
    await waitFor(() => screen.getByText("Rule 1"));

    const searchInput = screen.getByPlaceholderText(/Search rules.../i);
    fireEvent.change(searchInput, { target: { value: "Rule 2" } });

    expect(screen.queryByText("Rule 1")).not.toBeInTheDocument();
    expect(screen.getByText("Rule 2")).toBeInTheDocument();
  });

  test("filters rules based on status filter", async () => {
    render(<RulesTableNonEditable />);
    await waitFor(() => screen.getByText("Rule 1"));

    const statusFilter = screen.getByText(/Filter by status/i);
    fireEvent.click(statusFilter);
    fireEvent.click(screen.getByText(/Inactive/i));

    expect(screen.queryByText("Rule 1")).not.toBeInTheDocument();
    expect(screen.getByText("Rule 2")).toBeInTheDocument();
  });

  test("paginates rules correctly", async () => {
    render(<RulesTableNonEditable />);
    await waitFor(() => screen.getByText("Rule 1"));

    const nextPageButton = screen.getByRole("button", { name: /Next Page/i });
    fireEvent.click(nextPageButton);

    expect(screen.queryByText("Rule 1")).not.toBeInTheDocument();
    expect(screen.getByText("Rule 6")).toBeInTheDocument();
  });

  test("expands and collapses rule details", async () => {
    render(<RulesTableNonEditable />);
    await waitFor(() => screen.getByText("Rule 1"));

    const expandButton = screen.getAllByRole("button", { name: "" })[0];
    fireEvent.click(expandButton);

    expect(screen.getByText(/Description:/i)).toBeInTheDocument();
    fireEvent.click(expandButton);
    expect(screen.queryByText(/Description:/i)).not.toBeInTheDocument();
  });

  test("displays no rules found message when no rules match", async () => {
    render(<RulesTableNonEditable />);
    await waitFor(() => screen.getByText("Rule 1"));

    const searchInput = screen.getByPlaceholderText(/Search rules.../i);
    fireEvent.change(searchInput, { target: { value: "Nonexistent Rule" } });

    expect(screen.getByText(/No rules found/i)).toBeInTheDocument();
  });
});
