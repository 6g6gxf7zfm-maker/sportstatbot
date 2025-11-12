'use client'

import { useState } from 'react'
import { Settings as SettingsIcon, Save, Bell, Video, Hash } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    sports: {
      NBA: true,
      NFL: true,
      MLB: true,
      MLS: true,
      EPL: true,
      LaLiga: true,
      'Champions League': true,
      NHL: false,
    },
    viralScoreThreshold: 7,
    postsPerDay: 5,
    captionStyle: 'hype',
    outputDirectory: '~/Desktop/reels_ready',
  })

  const [saved, setSaved] = useState(false)

  function handleSave() {
    // In production, this would save to database
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your sports reel automation
        </p>
      </div>

      <div className="max-w-4xl">
        {/* Sports Preferences */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Video className="h-5 w-5" />
              Sports Preferences
            </h2>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-600 mb-4">
              Select which sports to monitor for highlights
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(settings.sports).map(([sport, enabled]) => (
                <label
                  key={sport}
                  className="flex items-center p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        sports: { ...settings.sports, [sport]: e.target.checked },
                      })
                    }
                    className="h-4 w-4 text-blue-600 rounded"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-900">
                    {sport}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Processing Settings */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <SettingsIcon className="h-5 w-5" />
              Processing Settings
            </h2>
          </div>
          <div className="p-6 space-y-6">
            {/* Viral Score Threshold */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Viral Score Threshold: {settings.viralScoreThreshold}/10
              </label>
              <input
                type="range"
                min="1"
                max="10"
                step="0.5"
                value={settings.viralScoreThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    viralScoreThreshold: parseFloat(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-1">
                Only process highlights with a viral score above this threshold
              </p>
            </div>

            {/* Posts Per Day */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Posts Per Day Target
              </label>
              <select
                value={settings.postsPerDay}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    postsPerDay: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {[3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                  <option key={num} value={num}>
                    {num} posts per day
                  </option>
                ))}
              </select>
            </div>

            {/* Output Directory */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Output Directory
              </label>
              <input
                type="text"
                value={settings.outputDirectory}
                onChange={(e) =>
                  setSettings({ ...settings, outputDirectory: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="~/Desktop/reels_ready"
              />
              <p className="text-xs text-gray-500 mt-1">
                Where processed reels will be saved
              </p>
            </div>
          </div>
        </div>

        {/* Caption Settings */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Hash className="h-5 w-5" />
              Caption Settings
            </h2>
          </div>
          <div className="p-6 space-y-6">
            {/* Caption Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Caption Style
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['hype', 'analytical', 'funny', 'casual'].map((style) => (
                  <label
                    key={style}
                    className={`
                      flex items-center justify-center p-3 border-2 rounded cursor-pointer
                      ${
                        settings.captionStyle === style
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      name="captionStyle"
                      value={style}
                      checked={settings.captionStyle === style}
                      onChange={(e) =>
                        setSettings({ ...settings, captionStyle: e.target.value })
                      }
                      className="sr-only"
                    />
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {style}
                    </span>
                  </label>
                ))}
              </div>
              <div className="mt-3 p-3 bg-gray-50 rounded">
                <p className="text-xs text-gray-700">
                  {settings.captionStyle === 'hype' &&
                    'Energetic and exciting with CAPS and emojis'}
                  {settings.captionStyle === 'analytical' &&
                    'Insightful and strategic, focusing on skill'}
                  {settings.captionStyle === 'funny' &&
                    'Humorous and entertaining with wordplay'}
                  {settings.captionStyle === 'casual' &&
                    'Conversational and relatable'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Posting Schedule */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Posting Schedule
            </h2>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-700 mb-4">Optimal posting times:</p>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {['07:30', '12:15', '18:00', '20:30', '22:00'].map((time) => (
                <div
                  key={time}
                  className="bg-blue-50 border border-blue-200 rounded p-3 text-center"
                >
                  <p className="text-lg font-semibold text-blue-900">{time}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-3">
              These times are optimized for maximum engagement based on Instagram
              best practices
            </p>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className={`
              px-6 py-3 rounded font-medium flex items-center gap-2
              ${
                saved
                  ? 'bg-green-600 text-white'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            <Save className="h-5 w-5" />
            {saved ? 'Settings Saved!' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
