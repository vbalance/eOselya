"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CalculationResult, Metrics } from "@/lib/api"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, ReferenceDot, Label } from 'recharts';

interface ResultsDashboardProps {
    results: CalculationResult
}

function MetricsCard({ title, value, suffix = "" }: { title: string, value: string | number, suffix?: string }) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}{suffix}</div>
            </CardContent>
        </Card>
    )
}

function formatCurrency(val: number) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
}

function formatPercent(val: number | null) {
    if (val === null) return "N/A";
    return (val * 100).toFixed(2) + "%";
}



export function ResultsDashboard({ results }: ResultsDashboardProps) {
    const scenarios = Object.keys(results);

    return (
        <div className="space-y-6">
            <Tabs defaultValue="base" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                    {scenarios.map(s => (
                        <TabsTrigger key={s} value={s} className="capitalize">{s}</TabsTrigger>
                    ))}
                </TabsList>

                {scenarios.map(scenario => {
                    const data = results[scenario];
                    const metrics = data.metrics;
                    const chartData = data.chart_data;

                    return (
                        <TabsContent key={scenario} value={scenario} className="space-y-6">
                            {/* METRICS GRID */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <MetricsCard title="Initial Investment" value={formatCurrency(metrics.initial_investment)} />
                                <MetricsCard title="NPV (with Sale)" value={formatCurrency(metrics.npv_with_sale)} />
                                <MetricsCard title="IRR (Annual)" value={formatPercent(metrics.irr_annual)} />
                                <MetricsCard title="ROI" value={formatPercent(metrics.roi)} />
                            </div>

                            {/* CHARTS */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* CASHFLOW CHART */}
                                <Card className="h-[400px]">
                                    <CardHeader>
                                        <CardTitle>Cumulative Cashflow (Operational, No Sale)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="h-[320px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={chartData} margin={{ right: 20 }}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="Month" />
                                                <YAxis tickFormatter={(val) => `$${val / 1000}k`} />
                                                <Tooltip formatter={(val: number) => formatCurrency(val)} />
                                                <Legend />
                                                <Area type="monotone" dataKey="Cumulative_NetCF_USD_nominal" stroke="#8884d8" fill="#8884d8" name="Cumulative Net CF" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>

                                {/* RENT VS MORTGAGE CHART */}
                                <Card className="h-[400px]">
                                    <CardHeader>
                                        <CardTitle>Rent vs Mortgage (Nominal USD)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="h-[320px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={chartData}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="Month" />
                                                <YAxis />
                                                <Tooltip formatter={(val: number) => formatCurrency(val)} />
                                                <Legend />
                                                <Line type="monotone" dataKey="Rent_USD_nominal" stroke="#82ca9d" name="Rent Income" />
                                                <Line type="monotone" dataKey="Mortgage_USD_nominal" stroke="#ff7300" name="Mortgage Payment" />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>

                                {/* PROPERTY VALUE CHART */}
                                <Card className="h-[400px] lg:col-span-2">
                                    <CardHeader>
                                        <CardTitle>Property Value Over Time (USD)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="h-[320px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 0 }}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="Month" />
                                                <YAxis tickFormatter={(val) => `$${val / 1000}k`} domain={['auto', 'auto']} />
                                                <Tooltip formatter={(val: number) => formatCurrency(val)} />
                                                <Legend />
                                                <Area type="monotone" dataKey="Property_Value_USD" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.2} name="Property Value" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </div>
                        </TabsContent>
                    )
                })}
            </Tabs>
        </div>
    )
}
