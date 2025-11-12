'use client'

import { useEffect, useState } from 'react'
import { getTodaysReels, type Reel } from '@/lib/supabase'
import { Play, Copy, Download, Calendar, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'

export default function DashboardPage() {
  const [reels, setReels] = useState<Reel[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedReel, setSelectedReel] = useState<Reel | null>(null)

  useEffect(() => {
    loadReels()
  }, [])

  async function loadReels() {
    setLoading(true)
    const data = await getTodaysReels()
    setReels(data)
    setLoading(false)
  }

  function copyCaption(caption: string) {
    navigator.clipboard.writeText(caption)
    alert('Caption copied to clipboard!')
  }

  const stats = {
    total: reels.length,
    avgScore: reels.length > 0
      ? (reels.reduce((sum, r) => sum + r.viral_score, 0) / reels.length).toFixed(1)
      : '0',
    topSport: reels.length > 0
      ? Object.entries(
          reels.reduce((acc, r) => {
            acc[r.sport] = (acc[r.sport] || 0) + 1
            return acc
          }, {} as Record<string, number>)
        ).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
      : 'N/A',
    ready: reels.filter(r => r.status === 'ready').length
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Today's processed reels and highlights
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Play className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Reels Created</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Viral Score</p>
              <p className="text-2xl font-bold text-gray-900">{stats.avgScore}/10</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Ready to Post</p>
              <p className="text-2xl font-bold text-gray-900">{stats.ready}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-orange-600 font-bold">🏆</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Top Sport</p>
              <p className="text-2xl font-bold text-gray-900">{stats.topSport}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Reels Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading reels...</p>
        </div>
      ) : reels.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Play className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No reels yet</h3>
          <p className="text-gray-600">
            Processed reels will appear here. Run the bot to create your first reels!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reels.map((reel) => (
            <div
              key={reel.id}
              className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Video Thumbnail */}
              <div className="relative bg-gray-900 aspect-[9/16]">
                {reel.thumbnail_url ? (
                  <img
                    src={reel.thumbnail_url}
                    alt={reel.headline || 'Reel thumbnail'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Play className="h-16 w-16 text-white opacity-50" />
                  </div>
                )}
                <div className="absolute top-2 right-2">
                  <span className="bg-blue-600 text-white px-2 py-1 rounded text-sm font-medium">
                    {reel.viral_score.toFixed(1)}/10
                  </span>
                </div>
                <div className="absolute top-2 left-2">
                  <span className="bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium">
                    {reel.sport}
                  </span>
                </div>
              </div>

              {/* Reel Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                  {reel.headline || 'Untitled Highlight'}
                </h3>

                {reel.teams.length > 0 && (
                  <p className="text-sm text-gray-600 mb-2">
                    {reel.teams.join(' vs ')}
                  </p>
                )}

                {reel.players.length > 0 && (
                  <p className="text-xs text-gray-500 mb-3">
                    {reel.players.join(', ')}
                  </p>
                )}

                {reel.caption && (
                  <div className="mb-3">
                    <p className="text-sm text-gray-700 line-clamp-3">
                      {reel.caption.split('\n')[0]}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedReel(reel)}
                    className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm font-medium hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <Play className="h-4 w-4" />
                    Preview
                  </button>
                  {reel.caption && (
                    <button
                      onClick={() => copyCaption(reel.caption!)}
                      className="bg-gray-100 text-gray-700 px-3 py-2 rounded text-sm font-medium hover:bg-gray-200"
                      title="Copy caption"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {selectedReel && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedReel(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedReel.headline}
                </h2>
                <button
                  onClick={() => setSelectedReel(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mb-4">
                <div className="bg-gray-100 rounded p-4">
                  <p className="text-sm font-medium text-gray-600 mb-2">Caption:</p>
                  <pre className="text-sm text-gray-900 whitespace-pre-wrap font-sans">
                    {selectedReel.caption}
                  </pre>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => copyCaption(selectedReel.caption!)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 flex items-center justify-center gap-2"
                >
                  <Copy className="h-4 w-4" />
                  Copy Caption
                </button>
                <a
                  href={selectedReel.local_path}
                  download
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded font-medium hover:bg-gray-700 flex items-center justify-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download Video
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
