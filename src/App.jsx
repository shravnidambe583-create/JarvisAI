import React, { useState } from 'react'
import HologramCanvas from './components/HologramCanvas'
import ChatHUD from './components/ChatHUD'
import { 
  TimeHeader, WeatherWidget, DiagnosticsWidget, 
  FocusWidget, VisionWidget, MissionWidget 
} from './components/Widgets'
import { Sparkles, Activity, ShieldAlert, Sliders } from 'lucide-react'
import { motion } from 'framer-motion'

export default function App() {
  const [hologramMode, setHologramMode] = useState(false)
  const [mood, setMood] = useState('happy') // happy, sad, excited, tired
  const [micActive, setMicActive] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState('')
  const [inputUrl, setInputUrl] = useState('')
  
  // Custom screen/vision query transmission triggers
  const [visionTrigger, setVisionTrigger] = useState('')

  const toggleHologram = () => setHologramMode(!hologramMode)

  const handleUrlSubmit = (e) => {
    e.preventDefault()
    setAvatarUrl(inputUrl.trim())
  }

  const handleExplainRequest = (queryText) => {
    setVisionTrigger(queryText + ` [Trigger Time: ${new Date().toLocaleTimeString()}]`)
  }

  return (
    <div className="relative w-screen h-screen bg-[#020208] text-slate-100 overflow-hidden font-sans select-none">
      
      {/* Tech Grid Underlay Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(6,10,32,0.6)_0%,rgba(2,2,8,1)_100%)] z-0 pointer-events-none" />
      
      {/* Sci-Fi CRT overlay elements */}
      <div className="scanline-overlay" />
      {hologramMode && <div className="hologram-scan" />}

      {/* 1. 3D Hologram canvas layer */}
      <HologramCanvas 
        hologramMode={hologramMode} 
        mood={mood} 
        micActive={micActive} 
        avatarUrl={avatarUrl}
      />

      {/* 2. HUD Grid Panels overlay */}
      <div className="dashboard-grid w-full h-full p-4 gap-4 relative z-10">
        
        {/* Top Header Widget */}
        <div className="grid col-span-3 items-center">
          <TimeHeader />
        </div>

        {/* LEFT COLUMN: System info and missions */}
        <div className="flex flex-col gap-4 overflow-y-auto max-h-[85vh] pr-2">
          <WeatherWidget />
          <DiagnosticsWidget />
          <MissionWidget />
        </div>

        {/* CENTER COLUMN: Spacer for 3D hologram Canvas */}
        <div className="relative flex flex-col justify-between items-center pointer-events-none">
          {/* Top Center Active HUD state indicator */}
          <div className="bg-black/60 border border-cyan-500/20 px-4 py-1.5 rounded-full flex items-center gap-2 mt-2 font-mono text-[10px] tracking-wider text-cyan-400 backdrop-blur-md">
            <Activity className="w-3.5 h-3.5 animate-pulse" />
            AVATAR MATRIX STATE: {mood.toUpperCase()}
          </div>

          {/* Bottom Center Chat Panel HUD */}
          <div className="w-full max-w-4xl pb-4">
            <ChatHUD 
              setMood={setMood} 
              setMicActive={setMicActive}
              setHologramMode={setHologramMode}
              inputTrigger={visionTrigger}
            />
          </div>
        </div>

        {/* RIGHT COLUMN: Productivity, Vision, Settings */}
        <div className="flex flex-col gap-4 overflow-y-auto max-h-[85vh] pl-2">
          <FocusWidget />
          <VisionWidget onExplainRequest={handleExplainRequest} />

          {/* Hologram / Settings Panel */}
          <motion.div 
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="glass-panel w-full interactive"
          >
            <div className="glass-panel-header">
              <span><Sliders className="inline w-4 h-4 mr-2" />MATRIX CONTROLLER</span>
              <span className="text-[10px] text-cyan-400 font-mono">PANEL</span>
            </div>
            <div className="p-3 space-y-3 font-mono text-xs">
              <button 
                onClick={toggleHologram}
                className={`w-full glow-button ${hologramMode ? 'glow-button-purple' : ''} py-2`}
              >
                {hologramMode ? 'DISABLE HOLOGRAM MATRIX' : 'ACTIVATE HOLOGRAM SHADER (H)'}
              </button>

              <form onSubmit={handleUrlSubmit} className="space-y-1.5 border-t border-slate-800 pt-3">
                <label className="text-[10px] text-slate-400">LOAD READY PLAYER ME GLB URL</label>
                <div className="flex gap-2">
                  <input 
                    type="url" 
                    value={inputUrl}
                    onChange={(e) => setInputUrl(e.target.value)}
                    placeholder="https://models.readyplayer.me/..."
                    className="flex-1 bg-black/30 border border-slate-700 rounded px-2 py-1 text-[11px] text-white focus:outline-none focus:border-cyan-400"
                  />
                  <button type="submit" className="glow-button py-1 px-2.5">Load</button>
                </div>
                {avatarUrl && (
                  <p className="text-[9px] text-green-400 truncate mt-1">ACTIVE: {avatarUrl}</p>
                )}
              </form>
            </div>
          </motion.div>
        </div>

      </div>
    </div>
  )
}
