import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, Sun, Cpu, Shield, Award, Play, Square, Volume2, 
  VolumeX, Camera, FileText, CheckSquare, Plus, RefreshCw, Zap,
  TrendingUp, Star, Award as Medal, Lock, Unlock, Grid
} from 'lucide-react'
import confetti from 'canvas-confetti'

// 1. Time / Clock Header
export function TimeHeader() {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="flex justify-between items-center w-full px-6 py-2 bg-black/40 border-b border-cyan-500/10 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <Zap className="w-5 h-5 text-cyan-400 animate-pulse" />
        <span className="font-mono text-xs tracking-widest text-cyan-400/80">JARVIS X INFINITY :: MAINFRAME ACTIVE</span>
      </div>
      <div className="flex items-center gap-6 font-mono text-sm">
        <span className="text-slate-400">{time.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}</span>
        <span className="text-cyan-400 font-bold tracking-wider">{time.toLocaleTimeString()}</span>
        <span className="px-2 py-0.5 text-[10px] bg-cyan-500/20 text-cyan-400 rounded border border-cyan-500/40">LATENCY: 8MS</span>
      </div>
    </div>
  )
}

// 2. Weather panel
export function WeatherWidget() {
  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="glass-panel w-full interactive"
    >
      <div className="glass-panel-header">
        <span><Sun className="inline w-4 h-4 mr-2" />METEOROLOGY SCAN</span>
        <span className="text-[10px] text-cyan-500/60 font-mono">LIVE FEED</span>
      </div>
      <div className="p-4 flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold text-white font-mono">24°C</h3>
          <p className="text-xs text-slate-400">Rainy / Cyber Storm Conditions</p>
          <p className="text-[10px] text-slate-500 font-mono mt-1">WIND: 14 KM/H | HUMIDITY: 78%</p>
        </div>
        <div className="w-12 h-12 rounded-full border border-cyan-500/20 flex items-center justify-center bg-cyan-500/5 animate-pulse">
          <Sun className="w-6 h-6 text-cyan-400" />
        </div>
      </div>
    </motion.div>
  )
}

// 3. Diagnostics & Future Prediction Dashboard
export function DiagnosticsWidget() {
  const [stats, setStats] = useState({ cpu: 22, ram: 48, battery: 100, temp: 42 })

  useEffect(() => {
    const interval = setInterval(() => {
      setStats({
        cpu: Math.floor(18 + Math.random() * 15),
        ram: Math.floor(45 + Math.random() * 6),
        battery: 100,
        temp: Math.floor(40 + Math.random() * 4)
      })
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.1 }}
      className="glass-panel w-full interactive"
    >
      <div className="glass-panel-header">
        <span><Cpu className="inline w-4 h-4 mr-2" />PREDICTION DASHBOARD</span>
        <span className="text-[10px] text-cyan-400/80 font-mono">FORECAST</span>
      </div>
      <div className="p-4 space-y-3 font-mono text-xs">
        {/* Core Stats */}
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>CPU WORKLOAD</span>
            <span className="text-cyan-400">{stats.cpu}%</span>
          </div>
          <div className="w-full h-1 bg-slate-900 rounded overflow-hidden">
            <div className="h-full bg-cyan-400 transition-all duration-500" style={{ width: `${stats.cpu}%` }}></div>
          </div>
        </div>

        {/* Future predictions */}
        <div className="border border-cyan-500/10 p-2.5 rounded bg-black/40 space-y-2 mt-2">
          <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>NEURAL HABIT PROJECTIONS</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-400 pt-1">
            <div>
              <p className="text-[9px] text-slate-500">FOCUS PEAK WINDOW</p>
              <p className="text-white font-bold mt-0.5">14:00 - 17:30</p>
            </div>
            <div>
              <p className="text-[9px] text-slate-500">EST. TASK COMPLETION</p>
              <p className="text-purple-400 font-bold mt-0.5">2.4 Hours Left</p>
            </div>
            <div>
              <p className="text-[9px] text-slate-500 font-mono">BATTERY WEAR RATE</p>
              <p className="text-green-400 font-bold mt-0.5">Optimal [Steady]</p>
            </div>
            <div>
              <p className="text-[9px] text-slate-500">LEARNING HABIT ACCURACY</p>
              <p className="text-cyan-400 font-bold mt-0.5">94.8% Match</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// 4. Pomodoro Focus Timer Widget
export function FocusWidget() {
  const [seconds, setSeconds] = useState(1500)
  const [isActive, setIsActive] = useState(false)
  const [mode, setMode] = useState('Work')
  const [lofiActive, setLofiActive] = useState(false)

  useEffect(() => {
    let interval = null
    if (isActive && seconds > 0) {
      interval = setInterval(() => {
        setSeconds(prev => prev - 1)
      }, 1000)
    } else if (seconds === 0) {
      setIsActive(false)
      confetti({ particleCount: 150, spread: 80 })
      if (mode === 'Work') {
        alert("Focus session complete! Stand by for break.")
        setMode('Break')
        setSeconds(300)
      } else {
        setMode('Work')
        setSeconds(1500)
      }
    }
    return () => clearInterval(interval)
  }, [isActive, seconds])

  const toggleTimer = () => setIsActive(!isActive)
  const resetTimer = () => {
    setIsActive(false)
    setSeconds(mode === 'Work' ? 1500 : 300)
  }

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60)
    const rem = secs % 60
    return `${mins.toString().padStart(2, '0')}:${rem.toString().padStart(2, '0')}`
  }

  return (
    <motion.div 
      initial={{ x: 50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="glass-panel w-full interactive"
    >
      <div className="glass-panel-header">
        <span><Shield className="inline w-4 h-4 mr-2" />FOCUS MODE</span>
        <span className="text-[10px] text-cyan-400 font-mono">{mode.toUpperCase()}</span>
      </div>
      <div className="p-4 text-center">
        <h2 className="text-4xl font-bold tracking-widest text-cyan-400 font-mono mb-2">
          {formatTime(seconds)}
        </h2>
        <div className="flex justify-center gap-3">
          <button onClick={toggleTimer} className="glow-button flex items-center gap-1 py-1 px-3">
            {isActive ? <Square className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            {isActive ? 'Pause' : 'Start'}
          </button>
          <button onClick={resetTimer} className="glow-button glow-button-purple py-1 px-3">
            Reset
          </button>
          <button 
            onClick={() => setLofiActive(!lofiActive)} 
            className={`glow-button py-1 px-2 flex items-center justify-center ${lofiActive ? 'bg-cyan-500/20 text-white' : ''}`}
            title="Toggle Lofi focus music"
          >
            {lofiActive ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
        </div>

        {lofiActive && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="text-[10px] text-cyan-400/80 font-mono mt-3 border-t border-cyan-500/10 pt-2"
          >
            🎵 STREAMING FOCUS MUSIC FEED...
            <iframe 
              src="https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&mute=0" 
              width="0" 
              height="0" 
              frameBorder="0" 
              allow="autoplay"
              className="absolute pointer-events-none opacity-0"
            />
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

// 5. Screen Vision Analysis Widget
export function VisionWidget({ onExplainRequest }) {
  const [image, setImage] = useState(null)
  const [scanning, setScanning] = useState(false)

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const triggerScan = () => {
    if (!image) return
    setScanning(true)
    setTimeout(() => {
      setScanning(false)
      onExplainRequest("[Vision Core OCR] Explain the code layout and resolve compiler warnings visible inside this console snapshot.")
    }, 2500)
  }

  return (
    <motion.div 
      initial={{ x: 50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.15 }}
      className="glass-panel w-full interactive"
    >
      <div className="glass-panel-header">
        <span><Camera className="inline w-4 h-4 mr-2" />SCREEN VISION SCANNER</span>
        <span className="text-[10px] text-purple-400 font-mono">OCR LOGIC</span>
      </div>
      <div className="p-4 space-y-3 font-mono text-xs">
        {!image ? (
          <label className="border border-dashed border-slate-700 hover:border-cyan-500/40 rounded-lg p-4 flex flex-col items-center justify-center gap-2 cursor-pointer bg-black/10 transition-colors">
            <Camera className="w-8 h-8 text-slate-500" />
            <span className="text-[10px] text-slate-400">DROP SNAPSHOT OR CLICK TO LOAD</span>
            <input type="file" onChange={handleImageChange} className="hidden" accept="image/*" />
          </label>
        ) : (
          <div className="relative border border-slate-800 rounded overflow-hidden h-28 bg-black">
            <img src={image} className="w-full h-full object-contain opacity-70" alt="Upload capture" />
            
            {scanning && (
              <motion.div 
                animate={{ top: ['0%', '100%', '0%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                className="absolute left-0 right-0 h-0.5 bg-cyan-400 shadow-[0_0_8px_#00f0ff] z-10"
              />
            )}
            
            <button 
              onClick={() => setImage(null)} 
              className="absolute top-1 right-1 bg-black/70 hover:bg-black text-[9px] px-1 py-0.5 rounded text-red-400"
            >
              Clear
            </button>
          </div>
        )}

        {image && (
          <button 
            onClick={triggerScan} 
            disabled={scanning}
            className="w-full glow-button py-1.5 flex items-center justify-center gap-2"
          >
            {scanning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
            {scanning ? 'SCANNING FRAMEWORK...' : 'TRANSLATE IMAGE'}
          </button>
        )}
      </div>
    </motion.div>
  )
}

// 6. Gamified Mission System & AI Skill Tree
export function MissionWidget({ xp, setXp, level, setLevel }) {
  const [tasks, setTasks] = useState([
    { id: 1, text: "Configure Flask premium female speech API", completed: true, points: 25 },
    { id: 2, text: "Interface gyroscopic 3D Worlds & Energy Core", completed: false, points: 50 },
    { id: 3, text: "Engage smart focus Pomodoro timer beats", completed: false, points: 25 },
    { id: 4, text: "Execute Screen Vision code OCR analysis", completed: false, points: 50 }
  ])
  const [newTask, setNewTask] = useState('')

  const handleToggle = (id) => {
    const updated = tasks.map(t => {
      if (t.id === id) {
        const completedState = !t.completed
        // Calculate XP gain/loss
        const gain = completedState ? t.points : -t.points
        const newXp = xp + gain
        
        // Handle level up
        if (newXp >= 100) {
          setLevel(prev => prev + 1)
          setXp(newXp - 100)
          confetti({ particleCount: 150, spread: 80, colors: ['#00f0ff', '#bf5af2'] })
        } else if (newXp < 0) {
          setXp(0)
        } else {
          setXp(newXp)
        }
        
        return { ...t, completed: completedState }
      }
      return t
    })
    setTasks(updated)
  }

  const handleAdd = (e) => {
    e.preventDefault()
    if (!newTask.trim()) return
    setTasks([...tasks, { id: Date.now(), text: newTask, completed: false, points: 25 }])
    setNewTask('')
  }

  // Skill Tree nodes
  const skillNodes = [
    { name: "Speech Link", reqLvl: 1, desc: "Neural audio TTS feedback loops" },
    { name: "Vision OCR", reqLvl: 2, desc: "Explain complex codes from files" },
    { name: "Clone Mainframe", reqLvl: 3, desc: "Split core into specialized clone nodes" }
  ]

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="glass-panel w-full interactive"
    >
      <div className="glass-panel-header">
        <span><Award className="inline w-4 h-4 mr-2 text-cyan-400" />MISSION DIRECTIVE</span>
        <span className="text-[10px] text-cyan-400 font-mono">LEVEL {level}</span>
      </div>
      
      <div className="p-3 space-y-3">
        {/* XP Level Progress Bar */}
        <div className="font-mono text-[10px] text-slate-400">
          <div className="flex justify-between mb-1">
            <span>EXPERIENCE POINT BUFFER</span>
            <span className="text-cyan-400">{xp}/100 XP</span>
          </div>
          <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-cyan-500/10 p-0.5">
            <div className="h-full bg-cyan-400 rounded-full transition-all duration-300" style={{ width: `${xp}%` }}></div>
          </div>
        </div>

        {/* Task Items */}
        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
          {tasks.map(t => (
            <div 
              key={t.id} 
              onClick={() => handleToggle(t.id)} 
              className="flex items-center justify-between cursor-pointer hover:bg-white/5 p-1 rounded transition-colors text-xs font-mono"
            >
              <div className="flex items-center gap-2">
                <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center ${t.completed ? 'border-cyan-400 bg-cyan-400/20' : 'border-slate-600'}`}>
                  {t.completed && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                </div>
                <span className={t.completed ? 'text-slate-500 line-through' : 'text-slate-300'}>{t.text}</span>
              </div>
              <span className={`text-[9px] ${t.completed ? 'text-slate-600' : 'text-cyan-500/70'}`}>+{t.points}XP</span>
            </div>
          ))}
        </div>
        
        {/* Skill Tree Matrix section */}
        <div className="border-t border-slate-800 pt-2 mt-1 space-y-2">
          <div className="flex items-center gap-1.5 text-purple-400 font-mono text-[10px] font-bold">
            <Grid className="w-3.5 h-3.5" />
            <span>AI COGNITIVE SKILL TREE</span>
          </div>
          
          <div className="grid grid-cols-3 gap-2">
            {skillNodes.map((s, idx) => {
              const unlocked = level >= s.reqLvl
              return (
                <div 
                  key={idx}
                  className={`p-1.5 rounded border flex flex-col items-center text-center transition-all ${
                    unlocked 
                      ? 'border-cyan-500/30 bg-cyan-500/5 text-cyan-200' 
                      : 'border-slate-800 bg-black/40 text-slate-500'
                  }`}
                  title={`${s.name}: ${s.desc} (Requires Level ${s.reqLvl})`}
                >
                  {unlocked ? <Unlock className="w-3.5 h-3.5 text-cyan-400 mb-1" /> : <Lock className="w-3.5 h-3.5 mb-1" />}
                  <span className="text-[8px] font-mono leading-tight">{s.name}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
