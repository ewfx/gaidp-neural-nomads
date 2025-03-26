import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, Download, BarChart2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const AnomalyDetectionResultsCard = () => {
    const parsedResults = typeof props.results === 'string' ? JSON.parse(props.results) : props.results;
    console.log(parsedResults)
    const [activeTab, setActiveTab] = useState('summary');

    const handleDownload = async () => {
        try {
            const response = await fetch(`http://localhost:5000/download/anamoly_result`, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'anomaly_detection_results.xlsx');
            document.body.appendChild(link);
            link.click();
            
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed', error);
            alert('Failed to download the file');
        }
    };

    const renderContent = () => {
        switch(activeTab) {
            case 'summary':
                return (
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-gray-100 p-4 rounded">
                            <h3 className="font-bold">Overview</h3>
                            <p>Total Anomalies: {parsedResults.total_anomalies}</p>
                            <p>AI Analysis Time: {parsedResults.ai_analysis_time.toFixed(2)} seconds</p>
                        </div>
                        <div className="bg-gray-100 p-4 rounded">
                            <h3 className="font-bold">Performance</h3>
                            <p>Timestamp: {new Date(parsedResults.timestamp).toLocaleString()}</p>
                        </div>
                    </div>
                );
            case 'details':
                return (
                    <div>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Anomaly ID</TableHead>
                                    <TableHead>Reason</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {parsedResults.raw_analysis ? 
                                    Object.entries(JSON.parse(parsedResults.raw_analysis)).map(([id, reason]) => (
                                        <TableRow key={id}>
                                            <TableCell>{id}</TableCell>
                                            <TableCell>{reason}</TableCell>
                                        </TableRow>
                                    )) : 
                                    <TableRow>
                                        <TableCell colSpan="2">No anomaly details available</TableCell>
                                    </TableRow>
                                }
                            </TableBody>
                        </Table>
                    </div>
                );
            case 'model':
                return (
                    <div className="bg-gray-100 p-4 rounded">
                        <h3 className="font-bold">Analysis Details</h3>
                        <p>Total Anomalies: {parsedResults.total_anomalies}</p>
                        <p>AI Analysis Time: {parsedResults.ai_analysis_time.toFixed(2)} seconds</p>
                        <p>Timestamp: {new Date(parsedResults.timestamp).toLocaleString()}</p>
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
                    {parsedResults.anomaly_rate > 5 ? (
                        <AlertTriangle className="text-red-500" />
                    ) : (
                        <CheckCircle2 className="text-green-500" />
                    )}
                    <CardTitle>Anomaly Detection Results</CardTitle>
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
                        { key: 'details', icon: <AlertTriangle className="mr-2 h-4 w-4" />, label: 'Anomaly Details' },
                        { key: 'model', icon: <BarChart2 className="mr-2 h-4 w-4" />, label: 'Model Info' }
                    ].map(tab => (
                        <Button 
                            key={tab.key}
                            variant={activeTab === tab.key ? 'default' : 'outline'}
                            onClick={() => setActiveTab(tab.key)}
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

export default AnomalyDetectionResultsCard;