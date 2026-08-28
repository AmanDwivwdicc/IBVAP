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
import { Upload, Loader2 } from 'lucide-react'
import { createClient } from '@/utils/supabase/client'

export function FaceUploadForm() {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')
  const [file, setFile] = useState<File | null>(null)

  const supabase = createClient()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !name) return

    setLoading(true)
    
    try {
      // 1. Upload the image directly to Supabase Storage
      const fileExt = file.name.split('.').pop()
      const fileName = `${crypto.randomUUID()}.${fileExt}`
      const filePath = `faces/${fileName}`

      const { error: uploadError } = await supabase.storage
        .from('evidence')
        .upload(filePath, file)

      if (uploadError) throw uploadError

      // 2. Generate a dummy 512d vector (since we don't have the Python ONNX worker right here in Next.js)
      // In a real system, the Python AI worker would pick up the insert event and generate the real embedding.
      // We insert the row so the UI updates immediately, and the worker fills in the real embedding later.
      const dummyVector = `[${Array.from({ length: 512 }, () => (Math.random() * 2 - 1).toFixed(4)).join(',')}]`

      const { error: dbError } = await supabase.from('known_faces').insert({
        name: name,
        description: 'Uploaded via Dashboard',
        threat_level: 'medium',
        reference_image_path: filePath,
        face_embedding: dummyVector
      })

      if (dbError) {
        // Rollback storage if DB insert fails
        await supabase.storage.from('evidence').remove([filePath])
        throw dbError
      }
      
      setOpen(false)
      window.location.reload() // Simple refresh to show new data
    } catch (error: unknown) {
      console.error(error)
      const msg = error instanceof Error ? error.message : 'Unknown error'
      alert(`Failed to upload face profile: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button className="gap-2" />}>
        <Upload className="h-4 w-4" /> Add Profile
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add Biometric Profile</DialogTitle>
            <DialogDescription>
              Upload a clear reference photo. The central AI will extract embedding vectors for edge comparison.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name/Alias
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3 bg-background"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="photo" className="text-right">
                Reference
              </Label>
              <Input
                id="photo"
                type="file"
                accept="image/jpeg,image/png"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="col-span-3 bg-background"
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {loading ? 'Processing Vector...' : 'Save Profile'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
