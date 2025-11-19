"use client"

import { useState } from "react"
import { InputForm } from "@/components/input-form"
import { ResultsDashboard } from "@/components/results-dashboard"
import { InvestmentInput, CalculationResult, calculateInvestment, exportInvestment } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function Home() {
  const [results, setResults] = useState<CalculationResult | null>(null)
  const [loading, setLoading] = useState(false) // Renamed from isLoading to loading
  const [error, setError] = useState<string | null>(null)
  const [lastInput, setLastInput] = useState<InvestmentInput | null>(null) // Added lastInput state

  const handleCalculate = async (data: InvestmentInput) => {
    setLoading(true)
    setError(null)
    setLastInput(data) // Save input for export
    try {
      const res = await calculateInvestment(data)
      setResults(res)
    } catch (err) {
      setError("Failed to calculate results. Please check your input.") // Updated error message
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Added handleExport function
  const handleExport = async () => {
    if (!lastInput) return
    try {
      const blob = await exportInvestment(lastInput)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'eOselya_Report.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (err) {
      console.error("Export failed", err)
      alert("Failed to export Excel report")
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 p-4 md:p-8"> {/* Updated styling */}
      <div className="max-w-7xl mx-auto space-y-8"> {/* Updated styling */}
        <div className="flex justify-between items-center"> {/* Updated structure for title and button */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">eOselya Investment Calculator</h1> {/* Updated title */}
            <p className="text-gray-500 mt-2">Analyze real estate investments with eOselya mortgage program</p> {/* Updated description */}
          </div>
          {results && ( // Conditionally render export button
            <Button onClick={handleExport} variant="outline" className="gap-2">
              <Download className="h-4 w-4" />
              Download Excel Report
            </Button>
          )}
        </div>

        {error && ( // Updated error display
          <div className="bg-red-50 text-red-600 p-4 rounded-md border border-red-200">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8"> {/* Changed xl to lg */}
          {/* LEFT COLUMN: INPUTS */}
          <div className="lg:col-span-1"> {/* Changed xl to lg */}
            <InputForm onCalculate={handleCalculate} isLoading={loading} /> {/* Changed isLoading to loading */}
          </div>

          {/* RIGHT COLUMN: RESULTS */}
          <div className="lg:col-span-2"> {/* Changed xl to lg */}
            {results ? (
              <ResultsDashboard results={results} />
            ) : (
              <div className="h-full flex items-center justify-center bg-white rounded-xl border border-gray-200 p-12 text-gray-400"> {/* Updated styling and text */}
                Enter parameters and click Calculate to see results
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
