'use client'

import { useEffect, useState } from 'react'
import { getPostingQueue, type PostingQueue } from '@/lib/supabase'
import { Calendar, Clock, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'

export default function QueuePage() {
  const [queue, setQueue] = useState<PostingQueue[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQueue()
  }, [])

  async function loadQueue() {
    setLoading(true)
    const data = await getPostingQueue()
    setQueue(data)
    setLoading(false)
  }

  const optimalTimes = ['07:30', '12:15', '18:00', '20:30', '22:00']

  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Posting Queue</h1>
        <p className="mt-2 text-gray-600">
          Scheduled reels and optimal posting times
        </p>
      </div>

      {/* Optimal Times Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Optimal Posting Times
        </h3>
        <div className="flex flex-wrap gap-3">
          {optimalTimes.map((time) => (
            <span
              key={time}
              className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium"
            >
              {time}
            </span>
          ))}
        </div>
        <p className="text-sm text-blue-700 mt-3">
          Schedule your posts during these times for maximum engagement
        </p>
      </div>

      {/* Queue List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading queue...</p>
        </div>
      ) : queue.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No scheduled posts</h3>
          <p className="text-gray-600">
            Add reels to your posting queue from the dashboard
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {queue.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded text-sm font-medium">
                      {item.reels?.sport || 'Unknown Sport'}
                    </span>
                    <span className="flex items-center text-sm text-gray-500">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      {item.reels?.viral_score.toFixed(1)}/10
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {item.reels?.headline || 'Untitled Highlight'}
                  </h3>

                  {item.reels?.teams && item.reels.teams.length > 0 && (
                    <p className="text-sm text-gray-600 mb-2">
                      {item.reels.teams.join(' vs ')}
                    </p>
                  )}

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {format(new Date(item.scheduled_time), 'MMM d, yyyy')}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {format(new Date(item.scheduled_time), 'h:mm a')}
                    </span>
                    <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                      Priority: {item.priority}
                    </span>
                  </div>
                </div>

                <div className="ml-4">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700">
                    Edit
                  </button>
                </div>
              </div>

              {item.notes && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600">{item.notes}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 mb-1">Total Scheduled</p>
          <p className="text-3xl font-bold text-gray-900">{queue.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 mb-1">Today</p>
          <p className="text-3xl font-bold text-gray-900">
            {queue.filter(item =>
              format(new Date(item.scheduled_time), 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd')
            ).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 mb-1">This Week</p>
          <p className="text-3xl font-bold text-gray-900">
            {queue.filter(item => {
              const scheduledDate = new Date(item.scheduled_time)
              const weekFromNow = new Date()
              weekFromNow.setDate(weekFromNow.getDate() + 7)
              return scheduledDate <= weekFromNow
            }).length}
          </p>
        </div>
      </div>
    </div>
  )
}
