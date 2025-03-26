import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import {
  ChevronLeft,
  ChevronRight,
  Search,
  ClipboardList,
  Filter,
  Download
} from "lucide-react";

export default function AnalysedTransaction(props) {
  const [allTransactions, setAllTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterExecuter, setFilterExecuter] = useState("all");
  const [showAudit, setShowAudit] = useState(false);
  const [auditId, setAuditId] = useState(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await fetch("http://localhost:5000/ddbanalysedTransaction");
        const data = await response.json();
        setAllTransactions(data.transactions || []);
        setFilteredTransactions(data.transactions || []);
      } catch (error) {
        console.error("Error fetching transactions:", error);
      }
    };

    fetchTransactions();
  }, []);

  const executerIds = [...new Set(allTransactions.map(tx => tx.executerId))];
  
  const downloadTransactions = () => {
    const link = document.createElement('a');
    link.href = '/temp_files/analysed_transactions.xlsx';
    link.download = 'analysed_transactions.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // Apply filters and search by Creating a new array to avoid mutation issues
  useEffect(() => {
    let result = [...allTransactions]; 
    
    // Apply executer filter
    if (filterExecuter && filterExecuter !== "all") {
      result = result.filter(tx => tx.executerId === filterExecuter);
    }
    
    if (searchTerm.trim() !== "") {
      const term = searchTerm.toLowerCase();
      result = result.filter(tx => 
        tx.id.toLowerCase().includes(term) || 
        tx.executerId.toLowerCase().includes(term) ||
        tx.date.includes(term)
      );
    }
    
    setFilteredTransactions(result);
    const maxPage = Math.max(1, Math.ceil(result.length / itemsPerPage));
    if (currentPage > maxPage){
      setCurrentPage(1);
    }else{
      setCurrentPage(currentPage);
    }
  }, [searchTerm, filterExecuter, allTransactions, itemsPerPage]);
  
  const goToPage = (pageNumber) => {
    const maxPage = Math.max(1, Math.ceil(filteredTransactions.length / itemsPerPage));
    const newPage = Math.min(Math.max(1, pageNumber), maxPage);
    setCurrentPage(newPage);
  };
  
  const handleItemsPerPageChange = (value) => {
    const newItemsPerPage = Number(value);
    setItemsPerPage(newItemsPerPage);
    
    const maxPage = Math.ceil(filteredTransactions.length / newItemsPerPage);
    if (currentPage > maxPage) {
      setCurrentPage(maxPage || 1);
    }
  };
  
  // Calculate pagination values
  const totalItems = filteredTransactions.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
  
  // Get current page data
  const paginatedTransactions = filteredTransactions.slice(startIndex, endIndex);
  
  const handleAudit = (id) => {
    setShowAudit(true);
    setAuditId(id);
    
    // Send message to Chainlit
    sendUserMessage(`Starting audit for ID: ${id}`);
  };
  
  // Reset audit view
  const resetAudit = () => {
    setShowAudit(false);
    setAuditId(null);
  };
  
  // Render audit view
  if (showAudit) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Auditing Transaction: {auditId}</span>
            <Button variant="outline" onClick={resetAudit}>
              Cancel Audit
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12">
            <ClipboardList className="h-16 w-16 mb-4 text-primary" />
            <p className="text-lg font-medium mb-2">Audit in progress</p>
            <p className="text-sm text-gray-500">
              The system is now auditing transaction {auditId}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // Render main transaction table
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Unaudited Transactions</CardTitle>
        <div className="flex flex-col gap-4 mt-4 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
            <Input
              placeholder="Search transactions..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <Select value={filterExecuter} onValueChange={setFilterExecuter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Filter Executer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Executers</SelectItem>
                {executerIds.map(id => (
                  <SelectItem key={id} value={id}>{id}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {filterExecuter !== "all" && (
              <Button 
                variant="outline" 
                size="icon" 
                onClick={() => setFilterExecuter("all")}
                title="Clear filter"
              >
                <Filter className="h-4 w-4" />
              </Button>
            )}
            
            <Button 
              variant="outline" 
              size="icon" 
              onClick={downloadTransactions}
              title="Download Analysed Transactions"
              disabled={filteredTransactions.length === 0}
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Table */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Executer ID</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedTransactions.length > 0 ? (
                paginatedTransactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell className="font-medium">{transaction.id}</TableCell>
                    <TableCell>{transaction.date}</TableCell>
                    <TableCell>{transaction.executerId}</TableCell>
                    <TableCell className="text-right">${transaction.amount.toLocaleString()}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleAudit(transaction.id)}
                      >
                        Audit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-6">
                    No transactions found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Pagination controls */}
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500">
            {totalItems > 0 ? (
              <>Showing {startIndex + 1}-{endIndex} of {totalItems}</>
            ) : (
              <>No items to show</>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Select 
              value={itemsPerPage.toString()} 
              onValueChange={handleItemsPerPageChange}
            >
              <SelectTrigger className="w-16">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <div className="text-sm">
              Page {currentPage} of {totalPages}
            </div>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}