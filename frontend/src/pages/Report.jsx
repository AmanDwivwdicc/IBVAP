import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import ReportViewer from '../components/ReportViewer'
import TopBar from '../components/TopBar'
import { api } from '../services/api'

export default function Report() {
  const { sessionId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!sessionId) return
    setLoading(true)
    api.getReport(sessionId)
      .then(setReport)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  return (
    <div className="min-h-screen p-4 space-y-4">
      <TopBar backendOnline={true} wsConnected={false} aiPipeline="stub" />

      <div className="flex items-center gap-4">
        <Link to="/" className="btn-secondary flex items-center gap-2 text-sm">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          Generating report...
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded">
          Failed to load report: {error}
        </div>
      )}

      {report && <ReportViewer report={report} />}
    </div>
  )
}
