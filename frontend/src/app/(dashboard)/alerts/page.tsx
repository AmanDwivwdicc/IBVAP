import { createClient } from '@/utils/supabase/server'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Search, Filter, Calendar } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default async function AlertsPage() {
  const supabase = await createClient()

  // Base query with joins
  const query = supabase
    .from('alerts')
    .select(`
      *,
      devices ( name, location ),
      cameras ( name )
    `)
    .order('timestamp', { ascending: false })
    .limit(50)

  // In a real app, apply filters from searchParams here
  // if (searchParams.feature) {
  //   query = query.eq('feature', searchParams.feature)
  // }

  const { data: alerts, error } = await query

  if (error) {
    console.error('Error fetching alerts:', error)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Security Alerts</h2>
          <p className="text-muted-foreground">
            Investigate historical events, intrusions, and detections.
          </p>
        </div>
        
        <div className="flex flex-1 items-center gap-2 md:max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search alerts..."
              className="pl-8 bg-background"
            />
          </div>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon">
            <Calendar className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <Card className="border-border/50">
        <div className="rounded-md border-0">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 border-b border-border/50 text-muted-foreground">
              <tr>
                <th className="h-10 px-4 text-left font-medium">Timestamp</th>
                <th className="h-10 px-4 text-left font-medium">Location / Device</th>
                <th className="h-10 px-4 text-left font-medium">Camera</th>
                <th className="h-10 px-4 text-left font-medium">Detections</th>
                <th className="h-10 px-4 text-left font-medium">Evidence</th>
                <th className="h-10 px-4 text-right font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {alerts?.map((alert) => (
                <tr key={alert.id} className="hover:bg-muted/20 transition-colors">
                  <td className="p-4">
                    <div className="font-medium">{new Date(alert.timestamp).toLocaleDateString()}</div>
                    <div className="text-xs text-muted-foreground">{new Date(alert.timestamp).toLocaleTimeString()}</div>
                  </td>
                  <td className="p-4">
                    <div className="font-medium">{alert.devices?.name || 'Unknown'}</div>
                    <div className="text-xs text-muted-foreground">{alert.devices?.location || 'Unknown loc'}</div>
                  </td>
                  <td className="p-4 text-muted-foreground">
                    {alert.cameras?.name || 'N/A'}
                  </td>
                  <td className="p-4">
                    <Badge variant="secondary" className="bg-secondary/50">
                      {alert.detection_count || 0} objects
                    </Badge>
                  </td>
                  <td className="p-4">
                    {alert.has_evidence ? (
                      <Badge variant="outline" className="border-primary/50 text-primary">Available</Badge>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <Link href={`/alerts/${alert.id}`}>
                      <Button variant="ghost" size="sm">Investigate</Button>
                    </Link>
                  </td>
                </tr>
              ))}
              {!alerts?.length && (
                <tr>
                  <td colSpan={6} className="h-32 text-center text-muted-foreground">
                    No alerts found matching the criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
