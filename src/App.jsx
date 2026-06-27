import React, { useState } from 'react'
import HologramCanvas from './components/HologramCanvas'
import ChatHUD from './components/ChatHUD'
import { 
  TimeHeader, WeatherWidget, DiagnosticsWidget, 
  FocusWidget, VisionWidget, MissionWidget 
} from './components/Widgets'
import { Sparkles, Activity, ShieldAlert, Sliders, Globe, Layers } from 'lucide-react'
import { motion } from 'framer-motion'

export default function App() {
  const [hologramMode, setHologramMode] = useState(false)
  const [mood, setMood] = useState('happy') // happy, sad, excited, tired
  const [micActive, setMicActive] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState('')
  const [inputUrl, setInputUrl] = useState('')
  
  // New States for Jarvis X Infinity
  const [world, setWorld] = useState('space-station') // space-station, cyber-city, iron-lab, neon-room, future-office
  const [cloneMode, setCloneMode] = useState(false)
  const [xp, setXp] = useState(25)
  const [level, setLevel] = useState(1)
  const [appBooted, setAppBooted] = useState(false)

  const [visionTrigger, setVisionTrigger] = useState('')

  const toggleHologram = () => setHologramMode(!hologramMode)

  const handleUrlSubmit = (e) => {
    e.preventDefault()
    setAvatarUrl(inputUrl.trim())
  }

  const handleExplainRequest = (queryText) => {
    setVisionTrigger(queryText + ` [Scan Time: ${new Date().toLocaleTimeString()}]`)
  }

  return (
    <div className="relative w-screen h-screen bg-[#020208] text-slate-100 overflow-hidden font-sans select-none">
      
      {/* Dynamic World Background Underlay Glow */}
      <div className={`absolute inset-0 z-0 pointer-events-none transition-all duration-1000 ${
        world === 'space-station' ? 'bg-[radial-gradient(ellipse_at_center,rgba(6,10,32,0.65)_0%,rgba(2,2,8,1)_100%)]' :
        world === 'cyber-city' ? 'bg-[radial-gradient(ellipse_at_center,rgba(32,6,20,0.65)_0%,rgba(2,2,8,1)_100%)]' :
        world === 'iron-lab' ? 'bg-[radial-gradient(ellipse_at_center,rgba(32,20,6,0.65)_0%,rgba(2,2,8,1)_100%)]' :
        world === 'neon-room' ? 'bg-[radial-gradient(ellipse_at_center,rgba(25,6,32,0.65)_0%,rgba(2,2,8,1)_100%)]' :
        'bg-[radial-gradient(ellipse_at_center,rgba(16,16,20,0.65)_0%,rgba(2,2,8,1)_100%)]'
      }`} />
      
      {/* CRT screen filters */}
      <div className="scanline-overlay" />
      {hologramMode && <div className="hologram-scan" />}

      {/* 1. 3D canvas stage */}
      <HologramCanvas 
        hologramMode={hologramMode} 
        mood={mood} 
        micActive={micActive} 
        avatarUrl={avatarUrl}
        world={world}
        cloneMode={cloneMode}
      />

      {/* 2. HUD Grid Panels overlay */}
      <div className="dashboard-grid w-full h-full p-4 gap-4 relative z-10">
        
        {/* Top Header */}
        <div className="grid col-span-3 items-center">
          <TimeHeader />
        </div>

        {/* LEFT COLUMN */}
        <div className="flex flex-col gap-4 overflow-y-auto max-h-[85vh] pr-2">
          <WeatherWidget />
          <DiagnosticsWidget />
          <MissionWidget xp={xp} setXp={setXp} level={level} setLevel={setLevel} />
        </div>

        {/* CENTER COLUMN */}
        <div className="relative flex flex-col justify-between items-center pointer-events-none">
          {/* Top Center active status bubble */}
          <div className="bg-black/60 border border-cyan-500/20 px-4 py-1.5 rounded-full flex items-center gap-2 mt-2 font-mono text-[10px] tracking-wider text-cyan-400 backdrop-blur-md">
            <Activity className="w-3.5 h-3.5 animate-pulse" />
            WORLD DIRECTIVE: {world.toUpperCase().replace('-', ' ')} | CORE: LEVEL {level}
          </div>

          {/* Bottom Chat Panel HUD */}
          <div className="w-full max-w-4xl pb-4">
            <ChatHUD 
              setMood={setMood} 
              setMicActive={setMicActive}
              setHologramMode={setHologramMode}
              inputTrigger={visionTrigger}
              appBooted={appBooted}
              setAppBooted={setAppBooted}
            />
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="flex flex-col gap-4 overflow-y-auto max-h-[85vh] pl-2">
          <FocusWidget />
          <VisionWidget onExplainRequest={handleExplainRequest} />

          {/* JARVIS X INFINITY Controller Matrix */}
          <motion.div 
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="glass-panel w-full interactive"
          >
            <div className="glass-panel-header">
              <span><Sliders className="inline w-4 h-4 mr-2" />INFINITY CONTROLLER</span>
              <span className="text-[10px] text-cyan-400 font-mono">CORE V2</span>
            </div>
            <div className="p-3 space-y-3 font-mono text-xs">
              
              {/* World Environment Selector */}
              <div className="space-y-1.5">
                <label className="text-[9px] text-slate-400 flex items-center gap-1">
                  <Globe className="w-3 h-3 text-cyan-400" />
                  <span>SELECT 3D WORLD GRID</span>
                </label>
                <select 
                  value={world} 
                  onChange={(e) => setWorld(e.target.value)}
                  className="w-full bg-black/40 border border-cyan-500/30 text-cyan-400 text-xs px-2.5 py-1.5 rounded focus:outline-none focus:border-cyan-400 font-mono cursor-pointer"
                >
                  <option value="space-station">WORLD: SPACE STATION</option>
                  <option value="cyber-city">WORLD: CYBER CITY</option>
                  <option value="iron-lab">WORLD: IRON MAN LAB</option>
                  <option value="neon-room">WORLD: VAPORWAVE NEON</option>
                  <option value="future-office">WORLD: MINIMAL OFFICE</option>
                </select>
              </div>

              {/* AI Clone Mode Toggle */}
              <div className="flex justify-between items-center border-t border-slate-800 pt-2.5">
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-white flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-purple-400" />
                    AI CLONE SUITE
                  </span>
                  <span className="text-[8px] text-slate-500">Spawn Coding & Research clones</span>
                </div>
                <button 
                  onClick={() => setCloneMode(!cloneMode)}
                  className={`px-3 py-1 rounded text-[10px] border transition-colors ${
                    cloneMode 
                      ? 'bg-purple-500/20 border-purple-500 text-purple-200' 
                      : 'bg-black/30 border-slate-700 text-slate-400 hover:border-purple-400 hover:text-purple-400'
                  }`}
                >
                  {cloneMode ? 'CLONES: ACTIVE' : 'DEPLOY CLONES'}
                </button>
              </div>

              <div className="border-t border-slate-800 pt-2.5 space-y-2">
                {/* Hologram Toggle */}
                <button 
                  onClick={toggleHologram}
                  className={`w-full glow-button ${hologramMode ? 'glow-button-purple' : ''} py-1.5 text-[11px]`}
                >
                  {hologramMode ? 'DISABLE HOLOGRAM SHADER' : 'ENTER TRANSPARENT HUD'}
                </button>

                {/* Ready Player Me URL */}
                <form onSubmit={handleUrlSubmit} className="space-y-1">
                  <label className="text-[8px] text-slate-500">LOAD READY PLAYER ME GLB URL</label>
                  <div className="flex gap-2">
                    <input 
                      type="url" 
                      value={inputUrl}
                      onChange={(e) => setInputUrl(e.target.value)}
                      placeholder="https://models.readyplayer.me/..."
                      className="flex-1 bg-black/30 border border-slate-700 rounded px-2 py-1 text-[10px] text-white focus:outline-none focus:border-cyan-400"
                    />
                    <button type="submit" className="glow-button py-1 px-2">Load</button>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>
        </div>

      </div>
    </div>
  )
}
