import { createClient } from '@/utils/supabase/server'
import { VirtualFenceCanvas, type Polygon } from '@/components/devices/VirtualFenceCanvas'
import { ChevronLeft } from 'lucide-react'
import Link from 'next/link'
import { notFound } from 'next/navigation'

export default async function DeviceSettingsPage({ params }: { params: Promise<{ id: string }> }) {
  const supabase = await createClient()

  const resolvedParams = await params
  const deviceId = resolvedParams.id

  const { data: device, error } = await supabase
    .from('devices')
    .select('*')
    .eq('id', deviceId)
    .single()

  if (error || !device) {
    notFound()
  }

  const { data: settings } = await supabase
    .from('device_settings')
    .select('settings')
    .eq('device_id', deviceId)
    .single()

  // In a real scenario, this would be a recent snapshot from the `alerts` or a dedicated `camera_snapshots` bucket.
  // Using a placeholder for the canvas background.
  const placeholderImageUrl = 'https://images.unsplash.com/photo-1558231221-a3f721524e9f?q=80&w=1200&auto=format&fit=crop'
  
  // Parse existing polygons if they exist
  const existingPolygons = settings?.settings && typeof settings.settings === 'object' && 'virtual_fences' in settings.settings
    ? (settings.settings as Record<string, unknown>).virtual_fences as Polygon[]
    : []

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/infrastructure" className="rounded-md p-2 hover:bg-muted text-muted-foreground transition-colors">
          <ChevronLeft className="h-5 w-5" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Configure: {device.name}</h2>
          <p className="text-muted-foreground">
            ID: {device.device_id}
          </p>
        </div>
      </div>

      <VirtualFenceCanvas 
        deviceId={deviceId} 
        referenceImageUrl={placeholderImageUrl}
        initialPolygons={existingPolygons}
      />
    </div>
  )
}
