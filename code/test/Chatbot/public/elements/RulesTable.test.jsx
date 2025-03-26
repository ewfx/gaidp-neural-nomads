import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import RulesTable from "@/Chatbot/public/elements/RulesTable";

describe("RulesTable Component", () => {
  it("renders the component and displays rules", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            rules: [
              {
                id: "1",
                name: "Rule 1",
                description: "Test Rule",
                status: "Active",
              },
            ],
          }),
      })
    );

    render(<RulesTable />);

    expect(await screen.findByText("Rules Table")).toBeInTheDocument();
    expect(await screen.findByText("Rule 1")).toBeInTheDocument();
  });

  it("filters rules by search term", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            rules: [
              {
                id: "1",
                name: "Rule 1",
                description: "Test Rule",
                status: "Active",
              },
            ],
          }),
      })
    );

    render(<RulesTable />);

    const searchInput = await screen.findByPlaceholderText("Search rules...");
    fireEvent.change(searchInput, { target: { value: "Rule 1" } });

    expect(await screen.findByText("Rule 1")).toBeInTheDocument();
  });

  it("handles edit and save actions", async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            rules: [
              {
                id: "1",
                name: "Rule 1",
                description: "Test Rule",
                status: "Active",
              },
            ],
          }),
      })
    );

    render(<RulesTable />);

    const editButton = await screen.findByText("Edit");
    fireEvent.click(editButton);

    const nameInput = await screen.findByDisplayValue("Rule 1");
    fireEvent.change(nameInput, { target: { value: "Updated Rule 1" } });

    const saveButton = await screen.findByText("Save");
    fireEvent.click(saveButton);

    expect(await screen.findByText("Updated Rule 1")).toBeInTheDocument();
  });
});
