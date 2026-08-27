import { createClient } from '@/utils/supabase/server'
import { Card, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Car, Search } from 'lucide-react'
import Link from 'next/link'
import { Input } from '@/components/ui/input'

export default async function WatchlistVehiclesPage() {
  const supabase = await createClient()

  const { data: plates, error } = await supabase
    .from('watchlist_plates')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching flagged plates:', error)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Intelligence: ANPR Watchlist</h2>
          <p className="text-muted-foreground">
            Manage flagged license plates for automatic detection and alerts.
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/intelligence/faces">
            <Button variant="outline">View Faces Watchlist</Button>
          </Link>
          <Button className="gap-2">
            <Car className="h-4 w-4" /> Add Plate
          </Button>
        </div>
      </div>

      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>Flagged Vehicles</CardTitle>
          <div className="relative max-w-sm mt-2">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search plate numbers..."
              className="pl-8 bg-background"
            />
          </div>
        </CardHeader>
        <div className="rounded-md border-t border-border/50">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 border-b border-border/50 text-muted-foreground">
              <tr>
                <th className="h-10 px-4 text-left font-medium">Plate Number</th>
                <th className="h-10 px-4 text-left font-medium">Threat Level</th>
                <th className="h-10 px-4 text-left font-medium">Description</th>
                <th className="h-10 px-4 text-left font-medium">Added</th>
                <th className="h-10 px-4 text-right font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {plates?.map((plate) => (
                <tr key={plate.id} className="hover:bg-muted/20 transition-colors">
                  <td className="p-4 font-mono font-bold text-lg tracking-wider">
                    {plate.plate_text}
                  </td>
                  <td className="p-4">
                    <Badge 
                      variant={plate.threat_level === 'critical' ? 'destructive' : 'secondary'}
                      className={plate.threat_level === 'high' ? 'bg-orange-500/10 text-orange-500' : ''}
                    >
                      {plate.threat_level?.toUpperCase() || 'UNKNOWN'}
                    </Badge>
                  </td>
                  <td className="p-4 text-muted-foreground max-w-[300px] truncate">
                    {plate.description || '-'}
                  </td>
                  <td className="p-4 text-muted-foreground">
                    {new Date(plate.created_at!).toLocaleDateString()}
                  </td>
                  <td className="p-4 text-right">
                    <Button variant="ghost" size="sm" className="text-destructive">Remove</Button>
                  </td>
                </tr>
              ))}
              {!plates?.length && (
                <tr>
                  <td colSpan={5} className="h-32 text-center text-muted-foreground">
                    No vehicles currently on the watchlist.
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
