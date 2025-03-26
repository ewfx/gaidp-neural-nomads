import React, { useState, useMemo } from 'react';
import { Download, BarChart2, AlertCircle, CheckCircle2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const ValidationResultsCard = () => {
    const parsedResults = typeof props.results === 'string' ? JSON.parse(props.results) : props.results;
  
    const [activeTab, setActiveTab] = useState('summary');
    const [ruleCurrentPage, setRuleCurrentPage] = useState(1);
    const [universalCurrentPage, setUniversalCurrentPage] = useState(1);
    const itemsPerPage = 5;
  
    const handleDownload = async () => {
        try {
          const identifier = parsedResults.identifier || parsedResults.rule_set;
          
          // Make fetch call to download endpoint
          const response = await fetch(`http://localhost:5000/download/${identifier}`, {
            method: 'GET'
          });

          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
    
          // Get the blob from the response
          const blob = await response.blob();
    
          // Create download link
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `${identifier}_validation_results.xlsx`);
          document.body.appendChild(link);
          link.click();
          
          // Clean up
          link.remove();
          window.URL.revokeObjectURL(url);
        } catch (error) {
          console.error('Download failed', error);
          alert('Failed to download the file');
        }
      };
    
  
     // Pagination logic for rule performance
     const paginatedRulePerformance = useMemo(() => {
        if (!parsedResults.rule_performance) return [];
        const startIndex = (ruleCurrentPage - 1) * itemsPerPage;
        return parsedResults.rule_performance.slice(startIndex, startIndex + itemsPerPage);
    }, [parsedResults.rule_performance, ruleCurrentPage]);

    const rulePerformanceTotalPages = useMemo(() => {
        return Math.ceil((parsedResults.rule_performance?.length || 0) / itemsPerPage);
    }, [parsedResults.rule_performance]);

    // Pagination logic for universal failure rules
    const paginatedUniversalFailureRules = useMemo(() => {
        if (!parsedResults.universal_failure_rules) return [];
        const startIndex = (universalCurrentPage - 1) * itemsPerPage;
        return parsedResults.universal_failure_rules.slice(startIndex, startIndex + itemsPerPage);
    }, [parsedResults.universal_failure_rules, universalCurrentPage]);

    const universalFailureTotalPages = useMemo(() => {
        return Math.ceil((parsedResults.universal_failure_rules?.length || 0) / itemsPerPage);
    }, [parsedResults.universal_failure_rules]);

    // Pagination component
    const PaginationControls = ({ currentPage, totalPages, onPageChange }) => (
        <div className="flex justify-center items-center space-x-2 mt-4">
            <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onPageChange(currentPage - 1)} 
                disabled={currentPage === 1}
            >
                <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm">
                Page {currentPage} of {totalPages}
            </span>
            <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onPageChange(currentPage + 1)} 
                disabled={currentPage === totalPages}
            >
                <ChevronRight className="h-4 w-4" />
            </Button>
        </div>
    );
  
    const renderContent = () => {
      switch(activeTab) {
        case 'summary':
          return (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-100 p-4 rounded">
                <h3 className="font-bold">Overview</h3>
                <p>Total Rules: {parsedResults.total_rules}</p>
                <p>Total Transactions: {parsedResults.total_transactions}</p>
                <p>Failed Transactions: {parsedResults.failed_transactions}</p>
                <p>Failure Rate: {parsedResults.failure_rate}%</p>
              </div>
              <div className="bg-gray-100 p-4 rounded">
                <h3 className="font-bold">Performance</h3>
                <p>Execution Time: {parsedResults.execution_time.toFixed(2)} seconds</p>
                <p>Timestamp: {new Date(parsedResults.timestamp).toLocaleString()}</p>
              </div>
            </div>
          );
        case 'rules':
          return (
            <div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rule ID</TableHead>
                    <TableHead>Rule Name</TableHead>
                    <TableHead>Failures</TableHead>
                    <TableHead>Failure Rate</TableHead>
                    <TableHead>Execution Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedRulePerformance.map((rule, index) => (
                    <TableRow key={index}>
                      <TableCell>{rule.rule_id}</TableCell>
                      <TableCell>{rule.rule_name}</TableCell>
                      <TableCell>{rule.failures}</TableCell>
                      <TableCell>{rule.failure_rate}%</TableCell>
                      <TableCell>{rule.execution_time.toFixed(3)} sec</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <PaginationControls 
                currentPage={ruleCurrentPage} 
                totalPages={rulePerformanceTotalPages}
                onPageChange={setRuleCurrentPage}
              />
            </div>
          );
        case 'universal':
          return (
            <div>
              <h3 className="font-bold mb-4">Universal Failure Rules</h3>
              {paginatedUniversalFailureRules.map((rule, index) => (
                <Card key={index} className="mb-2">
                  <CardHeader>
                    <CardTitle>{rule.rule_name || 'Unnamed Rule'}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>Rule ID: {rule.rule_id || 'N/A'}</p>
                    <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
                      {rule.sql_query || 'No SQL query available'}
                    </pre>
                  </CardContent>
                </Card>
              ))}
              <PaginationControls 
                currentPage={universalCurrentPage} 
                totalPages={universalFailureTotalPages}
                onPageChange={setUniversalCurrentPage}
              />
            </div>
          );
        default:
          return null;
      }
    };
  
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div className="flex items-center space-x-4">
            {parsedResults.failure_rate > 10 ? (
              <AlertCircle className="text-red-500" />
            ) : (
              <CheckCircle2 className="text-green-500" />
            )}
            <CardTitle>Data Validation Results</CardTitle>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" /> Download Results
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2 mb-4">
            {[
              { key: 'summary', icon: <BarChart2 className="mr-2 h-4 w-4" />, label: 'Summary' },
              { key: 'rules', icon: <AlertCircle className="mr-2 h-4 w-4" />, label: 'Rule Performance' },
              { key: 'universal', icon: <AlertCircle className="mr-2 h-4 w-4" />, label: 'Universal Failures' }
            ].map(tab => (
              <Button 
                key={tab.key}
                variant={activeTab === tab.key ? 'default' : 'outline'}
                onClick={() => {
                  setActiveTab(tab.key);
                  // Reset pagination when switching tabs
                  if (tab.key === 'rules') setRuleCurrentPage(1);
                  if (tab.key === 'universal') setUniversalCurrentPage(1);
                }}
              >
                {tab.icon}
                {tab.label}
              </Button>
            ))}
          </div>
          {renderContent()}
        </CardContent>
      </Card>
    );
  };
  
  export default ValidationResultsCard;