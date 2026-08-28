'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { PlusCircle, Loader2, Copy, CheckCircle2 } from 'lucide-react'

export function DeviceRegistrationForm() {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const [deviceId, setDeviceId] = useState('')
  const [name, setName] = useState('')
  const [location, setLocation] = useState('')
  const [cameraId, setCameraId] = useState('')
  const [cameraName, setCameraName] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  
  const [credentials, setCredentials] = useState<{ DEVICE_EMAIL: string, DEVICE_PASSWORD: string } | null>(null)
  const [copied, setCopied] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!deviceId) return

    setLoading(true)
    setCredentials(null)
    
    try {
      const bodyData: Record<string, unknown> = {
        device_id: deviceId,
        name: name || undefined,
        location: location || undefined
      }

      if (cameraId) {
        bodyData.cameras = [
          {
            camera_id: cameraId,
            name: cameraName || undefined,
            source_url: sourceUrl || undefined
          }
        ]
      }

      const res = await fetch('/api/devices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
      })

      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed')
      }
      
      setCredentials(data.credentials)
    } catch (error: unknown) {
      console.error(error)
      const errMessage = error instanceof Error ? error.message : 'Unknown error'
      alert(`Error: ${errMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (credentials) {
      navigator.clipboard.writeText(`DEVICE_EMAIL=${credentials.DEVICE_EMAIL}\nDEVICE_PASSWORD=${credentials.DEVICE_PASSWORD}`)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleClose = () => {
    setOpen(false)
    if (credentials) {
      window.location.reload()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(val) => {
      // Prevent closing by clicking outside if they haven't copied the credentials
      if (!val && credentials) return
      setOpen(val)
    }}>
      <DialogTrigger render={<Button className="gap-2" />}>
        <PlusCircle className="h-4 w-4" /> Register Edge Device
      </DialogTrigger>
      <DialogContent className="sm:max-w-[450px]">
        {!credentials ? (
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Register Edge Device</DialogTitle>
              <DialogDescription>
                Provision a new hardware node for the border network. A unique API key will be generated.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="deviceId" className="text-right">
                  Device ID <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="deviceId"
                  placeholder="e.g. edge-bop-004"
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  className="col-span-3 bg-background font-mono text-sm"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right">
                  Name
                </Label>
                <Input
                  id="name"
                  placeholder="North Post Alpha"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="col-span-3 bg-background"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="location" className="text-right">
                  Location
                </Label>
                <Input
                  id="location"
                  placeholder="Sector 7G"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="col-span-3 bg-background"
                />
              </div>

              <div className="pt-2 pb-2">
                <h4 className="text-sm font-medium border-b border-border pb-1">Initial Camera (Optional)</h4>
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="cameraId" className="text-right">
                  Camera ID
                </Label>
                <Input
                  id="cameraId"
                  placeholder="cam-01"
                  value={cameraId}
                  onChange={(e) => setCameraId(e.target.value)}
                  className="col-span-3 bg-background font-mono text-sm"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="cameraName" className="text-right">
                  Camera Name
                </Label>
                <Input
                  id="cameraName"
                  placeholder="Main Gate Cam"
                  value={cameraName}
                  onChange={(e) => setCameraName(e.target.value)}
                  className="col-span-3 bg-background"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="sourceUrl" className="text-right">
                  Stream URL
                </Label>
                <Input
                  id="sourceUrl"
                  placeholder="rtsp://..."
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  className="col-span-3 bg-background"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={loading || !deviceId}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Provision Device
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <div className="space-y-6 py-4">
            <DialogHeader>
              <DialogTitle className="text-green-500 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5" /> Provisioning Successful
              </DialogTitle>
              <DialogDescription className="text-foreground font-medium pt-2">
                Copy these credentials into the device&apos;s `.env` file.
              </DialogDescription>
            </DialogHeader>
            
            <div className="bg-destructive/10 border border-destructive/20 text-destructive p-3 rounded-md text-sm">
              <strong>Warning:</strong> For security reasons, the password is not stored in plaintext. If you lose it, you must register a new device or reset credentials via Supabase.
            </div>

            <div className="flex flex-col gap-2 relative">
              <div className="flex flex-col gap-1">
                <Label className="text-xs text-muted-foreground">DEVICE_EMAIL</Label>
                <Input readOnly value={credentials.DEVICE_EMAIL} className="font-mono bg-muted text-xs" />
              </div>
              <div className="flex flex-col gap-1">
                <Label className="text-xs text-muted-foreground">DEVICE_PASSWORD</Label>
                <Input readOnly value={credentials.DEVICE_PASSWORD} className="font-mono bg-muted text-xs" />
              </div>
              <Button variant="secondary" size="icon" onClick={handleCopy} className="absolute top-6 right-0 h-14 rounded-l-none">
                {copied ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            
            <DialogFooter>
              <Button onClick={handleClose} className="w-full">
                I have copied the credentials
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
