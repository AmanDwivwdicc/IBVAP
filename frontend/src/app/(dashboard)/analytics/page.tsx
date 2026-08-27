import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { BarChart3, LineChart, PieChart } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Analytics & Reports</h2>
        <p className="text-muted-foreground">
          Historical trends, hot-spots, and system performance metrics.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="col-span-2 border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <LineChart className="h-4 w-4" />
              Intrusions Over Time (Last 30 Days)
            </CardTitle>
            <CardDescription>Daily alert volume aggregated across all border devices.</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px] flex items-center justify-center border-t border-border/50 bg-muted/10">
            <div className="text-muted-foreground flex flex-col items-center gap-2">
              <BarChart3 className="h-8 w-8 opacity-50" />
              <span>Chart integration pending (Recharts)</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <PieChart className="h-4 w-4" />
              Detection Breakdown
            </CardTitle>
            <CardDescription>Distribution by classification type.</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px] flex items-center justify-center border-t border-border/50 bg-muted/10">
            <div className="text-muted-foreground flex flex-col items-center gap-2">
              <PieChart className="h-8 w-8 opacity-50" />
              <span>Distribution Data</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
