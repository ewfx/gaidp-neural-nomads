import { useState, useEffect } from "react";

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Table Components
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Icons
import {
  ChevronLeft,
  ChevronRight,
  Search,
  ChevronDown,
  Trash2,
} from "lucide-react";

// Select Components
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const RulesTable = () => {
  const [rules, setRules] = useState([]);
  const [editId, setEditId] = useState(null);
  const [editedRule, setEditedRule] = useState({});
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [expandedRule, setExpandedRule] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const rowsPerPage = 5;

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await fetch(`http://localhost:5000/rules/${props.identifier}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log("Response:", response);
        const data = await response.json();
        setRules(data.rules);
      } catch (error) {
        console.error("Error fetching rules:", error);
      }
    };
  
    fetchRules();
  }, []);

  const filteredRules = rules.filter((rule) => {
    const matchesSearch =
      search === "" ||
      rule.name.toLowerCase().includes(search.toLowerCase()) ||
      rule.description.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "all" ||
      rule.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  const paginatedRules = filteredRules.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const totalPages = Math.ceil(filteredRules.length / rowsPerPage);

  const handleEdit = (id) => {
    setEditId(id);
    const ruleToEdit = rules.find((r) => r.id === id);
    setEditedRule({ ...ruleToEdit });

    // Auto-expand the rule when editing
    setExpandedRule(id);
  };

  const handleSave = async () => {
    try {
      // Update the local state first
      const updatedRules = rules.map((r) => (r.id === editId ? editedRule : r));
      setRules(updatedRules);
      setEditId(null);

      // Call the update API for each edited field using fetch
      for (const [field_name, value] of Object.entries(editedRule)) {
        const response = await fetch(`http://localhost:5000/rules/${props.identifier}/${editId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ field_name, value }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data.message);
      }
    } catch (error) {
      console.error("Error saving rule:", error);
    }
  };
  

  const handleCancel = () => {
    setEditId(null);
    setEditedRule({});
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEditedRule((prev) => ({ ...prev, [name]: value }));
  };

  const toggleExpand = (id) => {
    setExpandedRule(expandedRule === id ? null : id);
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1); // Reset to first page when search changes
  };

  const handleStatusFilterChange = (value) => {
    setStatusFilter(value);
    setPage(1); // Reset to first page when filter changes
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`http://localhost:5000/rules/${props.identifier}/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data.message);

      // Update the local state after successful deletion
      const updatedRules = rules.filter((rule) => rule.id !== id);
      setRules(updatedRules);

      // If expanded rule is deleted, clear the expanded state
      if (expandedRule === id) {
        setExpandedRule(null);
      }

      // If we're on a page that would now be empty, go to the previous page
      const newTotalPages = Math.ceil((filteredRules.length - 1) / rowsPerPage);
      if (page > newTotalPages && newTotalPages > 0) {
        setPage(newTotalPages);
      }
    } catch (error) {
      console.error("Error deleting rule:", error);
    }
  };

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl">Rules Table</CardTitle>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative flex w-full max-w-sm items-center">
            <Search className="absolute left-2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search rules..."
              className="pl-8"
              value={search}
              onChange={handleSearchChange}
            />
          </div>
          <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
            <SelectTrigger className="w-36">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16 text-center">Rule No</TableHead>
                <TableHead>Name</TableHead>
                <TableHead className="hidden md:table-cell">
                  Description
                </TableHead>
                <TableHead className="w-24">Status</TableHead>
                <TableHead className="w-32 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedRules.length > 0 ? (
                paginatedRules.map((rule) => (
                  <React.Fragment key={rule.id}>
                    <TableRow className="hover:bg-gray-50">
                      <TableCell className="text-center font-medium">
                        {rule.id}
                      </TableCell>
                      <TableCell>
                        {editId === rule.id ? (
                          <Input
                            name="name"
                            value={editedRule.name}
                            onChange={handleChange}
                          />
                        ) : (
                          <div className="flex items-center gap-2">
                            {rule.name}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleExpand(rule.id)}
                              className="p-0 h-6 w-6"
                            >
                              <ChevronDown
                                className={`h-4 w-4 transition-transform ${
                                  expandedRule === rule.id
                                    ? "transform rotate-180"
                                    : ""
                                }`}
                              />
                            </Button>
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        {editId === rule.id ? (
                          <Textarea
                            name="description"
                            value={editedRule.description}
                            onChange={handleChange}
                            rows={2}
                          />
                        ) : rule.description.length > 50 ? (
                          `${rule.description.slice(0, 50)}...`
                        ) : (
                          rule.description
                        )}
                      </TableCell>
                      <TableCell>
                        {editId === rule.id ? (
                          <Select
                            defaultValue={editedRule.status.toLowerCase()}
                            onValueChange={(value) =>
                              setEditedRule({
                                ...editedRule,
                                status:
                                  value.charAt(0).toUpperCase() +
                                  value.slice(1),
                              })
                            }
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="active">Active</SelectItem>
                              <SelectItem value="inactive">Inactive</SelectItem>
                            </SelectContent>
                          </Select>
                        ) : (
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              rule.status === "Active"
                                ? "bg-green-100 text-green-800"
                                : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {rule.status}
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        {editId === rule.id ? (
                          <div className="flex justify-end gap-2">
                            <Button size="sm" onClick={handleSave} disabled={!props.isAdmin}>
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={handleCancel}
                              disabled={!props.isAdmin}
                            >
                              Cancel
                            </Button>
                          </div>
                        ) : (
                          <div className="flex justify-end gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleEdit(rule.id)}
                              disabled={!props.isAdmin}
                            >
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDelete(rule.id)}
                              disabled={!props.isAdmin}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                    {(expandedRule === rule.id || editId === rule.id) && (
                      <TableRow>
                        <TableCell colSpan={5} className="p-0">
                          <div className="p-4 bg-gray-900 border-t">
                            <div className="grid gap-3">
                              <div>
                                <h4 className="font-medium text-sm">
                                  Description:
                                </h4>
                                {editId === rule.id ? (
                                  <Textarea
                                    name="description"
                                    value={editedRule.description}
                                    onChange={handleChange}
                                    rows={3}
                                    className="mt-2 w-full"
                                  />
                                ) : (
                                  <p className="text-sm">{rule.description}</p>
                                )}
                              </div>
                              {rule.sql && (
                                <div>
                                  <h4 className="font-medium text-sm">
                                    SQL Query:
                                  </h4>
                                  <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                                    {rule.sql}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No rules found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between space-x-2 py-4">
          <div className="text-sm text-gray-500">
            Showing{" "}
            {filteredRules.length > 0 ? (page - 1) * rowsPerPage + 1 : 0}-
            {Math.min(page * rowsPerPage, filteredRules.length)} of{" "}
            {filteredRules.length} rules
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              <span className="sr-only">Previous Page</span>
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                // Show first page, last page, current page, and pages around current
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (page <= 3) {
                  pageNum = i + 1;
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = page - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={page === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => setPage(pageNum)}
                    className="w-8 h-8 p-0"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages || totalPages === 0}
            >
              <ChevronRight className="h-4 w-4" />
              <span className="sr-only">Next Page</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default RulesTable;