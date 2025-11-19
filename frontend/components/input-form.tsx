"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { InvestmentInput } from "@/lib/api"

interface InputFormProps {
    onCalculate: (data: InvestmentInput) => void
    isLoading: boolean
}

const defaultInput: InvestmentInput = {
    apartment_cost_usd: 57000,
    fx_today: 41.5,
    downpayment_usd: 11500,
    extra_purchase_costs_usd: 5000,
    loan_term_years: 20,
    interest_annual: 0.07,
    payment_type: 'differentiated',
    rent_initial_uah: 12000,
    insurance_annual: 0.0025,
    amortization_coefficient: 1.0,
    usd_discount_annual: 0.03,
    scenarios: {
        pessimistic: { rent_growth_annual: -0.01, inflation_uah_annual: 0.07, price_growth_annual_usd: -0.01 },
        base: { rent_growth_annual: 0.0, inflation_uah_annual: 0.10, price_growth_annual_usd: 0.0 },
        optimistic: { rent_growth_annual: 0.03, inflation_uah_annual: 0.13, price_growth_annual_usd: 0.02 }
    }
}

export function InputForm({ onCalculate, isLoading }: InputFormProps) {
    const [data, setData] = useState<InvestmentInput>(defaultInput)

    const handleChange = (field: keyof InvestmentInput, value: any) => {
        setData(prev => ({ ...prev, [field]: value }))
    }

    const handleScenarioChange = (scenario: string, field: string, value: number) => {
        setData(prev => ({
            ...prev,
            scenarios: {
                ...prev.scenarios,
                [scenario]: {
                    ...prev.scenarios[scenario],
                    [field]: value
                }
            }
        }))
    }

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Investment Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">

                <Tabs defaultValue="object" className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="object">Object</TabsTrigger>
                        <TabsTrigger value="loan">Loan</TabsTrigger>
                        <TabsTrigger value="rent">Rent</TabsTrigger>
                        <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
                    </TabsList>

                    {/* OBJECT TAB */}
                    <TabsContent value="object" className="space-y-4 pt-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Apartment Cost (USD)</Label>
                                <Input
                                    type="number"
                                    value={data.apartment_cost_usd}
                                    onChange={e => handleChange('apartment_cost_usd', Number(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>FX Rate (UAH/USD)</Label>
                                <Input
                                    type="number"
                                    value={data.fx_today}
                                    onChange={e => handleChange('fx_today', Number(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Down Payment (USD)</Label>
                                <Input
                                    type="number"
                                    value={data.downpayment_usd}
                                    onChange={e => handleChange('downpayment_usd', Number(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Extra Costs (USD)</Label>
                                <Input
                                    type="number"
                                    value={data.extra_purchase_costs_usd}
                                    onChange={e => handleChange('extra_purchase_costs_usd', Number(e.target.value))}
                                />
                            </div>
                        </div>
                    </TabsContent>

                    {/* LOAN TAB */}
                    <TabsContent value="loan" className="space-y-4 pt-4">
                        <div className="space-y-2">
                            <Label>Loan Term: {data.loan_term_years} years</Label>
                            <Slider
                                value={[data.loan_term_years]}
                                min={1} max={30} step={1}
                                onValueChange={vals => handleChange('loan_term_years', vals[0])}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Interest Rate (Annual)</Label>
                                <div className="flex items-center gap-2">
                                    <Input
                                        type="number" step="0.001"
                                        value={data.interest_annual}
                                        onChange={e => handleChange('interest_annual', Number(e.target.value))}
                                    />
                                    <span className="text-sm text-muted-foreground">{(data.interest_annual * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Payment Type</Label>
                                <div className="flex items-center space-x-2 pt-2">
                                    <Label htmlFor="payment-mode">Diff</Label>
                                    <Switch
                                        id="payment-mode"
                                        checked={data.payment_type === 'annuity'}
                                        onCheckedChange={checked => handleChange('payment_type', checked ? 'annuity' : 'differentiated')}
                                    />
                                    <Label htmlFor="payment-mode">Annuity</Label>
                                </div>
                            </div>
                        </div>
                    </TabsContent>

                    {/* RENT TAB */}
                    <TabsContent value="rent" className="space-y-4 pt-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Initial Rent (UAH)</Label>
                                <Input
                                    type="number"
                                    value={data.rent_initial_uah}
                                    onChange={e => handleChange('rent_initial_uah', Number(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="amortization_coefficient">Amortization</Label>
                                <Input
                                    type="number" step="0.1"
                                    value={data.amortization_coefficient}
                                    onChange={e => handleChange('amortization_coefficient', Number(e.target.value))}
                                />
                                <p className="text-xs text-muted-foreground">Months of rent per year spent on repairs/maintenance</p>
                            </div>
                        </div>
                    </TabsContent>

                    {/* SCENARIOS TAB */}
                    <TabsContent value="scenarios" className="space-y-4 pt-4">
                        {['base', 'pessimistic', 'optimistic'].map(scenario => (
                            <div key={scenario} className="border rounded p-3 space-y-2">
                                <h4 className="font-semibold capitalize">{scenario} Scenario</h4>
                                <div className="grid grid-cols-3 gap-2 text-sm">
                                    <div>
                                        <Label className="text-xs">Rent Growth</Label>
                                        <Input
                                            type="number" step="0.01"
                                            value={data.scenarios[scenario].rent_growth_annual}
                                            onChange={e => handleScenarioChange(scenario, 'rent_growth_annual', Number(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-xs">Inflation UAH</Label>
                                        <Input
                                            type="number" step="0.01"
                                            value={data.scenarios[scenario].inflation_uah_annual}
                                            onChange={e => handleScenarioChange(scenario, 'inflation_uah_annual', Number(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-xs">Price Growth USD</Label>
                                        <Input
                                            type="number" step="0.01"
                                            value={data.scenarios[scenario].price_growth_annual_usd}
                                            onChange={e => handleScenarioChange(scenario, 'price_growth_annual_usd', Number(e.target.value))}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </TabsContent>
                </Tabs>

                <Button className="w-full" onClick={() => onCalculate(data)} disabled={isLoading}>
                    {isLoading ? "Calculating..." : "Calculate Investment"}
                </Button>
            </CardContent>
        </Card>
    )
}
