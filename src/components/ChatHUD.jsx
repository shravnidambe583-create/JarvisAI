import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Mic, MicOff, Volume2, User, HelpCircle, Terminal, RefreshCw } from 'lucide-react'

// Custom Typewriter text animation
function TypewriterText({ text, speed = 15 }) {
  const [displayText, setDisplayText] = useState('')
  
  useEffect(() => {
    let i = 0
    setDisplayText('')
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayText(prev => prev + text.charAt(i))
        i++
      } else {
        clearInterval(timer)
      }
    }, speed)
    return () => clearInterval(timer)
  }, [text, speed])

  return <span>{displayText}</span>
}

export default function ChatHUD({ setMood, setMicActive, setHologramMode, inputTrigger, appBooted, setAppBooted }) {
  const [messages, setMessages] = useState([
    { sender: 'jarvis', text: "Welcome back. All systems are online. How may I assist you today?", time: new Date() }
  ])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [voiceActive, setVoiceActive] = useState(false)
  const [voiceProfile, setVoiceProfile] = useState('en-US-EmmaMultilingualNeural')
  const [muteTextToSpeech, setMuteTextToSpeech] = useState(false)
  
  const audioRef = useRef(null)
  const chatEndRef = useRef(null)

  // Autoplay voice greeting on boot (after user click interaction)
  useEffect(() => {
    if (appBooted) {
      speakText("Welcome back. All systems are online. How may I assist you today?", voiceProfile)
    }
  }, [appBooted])

  // Listen for screen vision/external triggers
  useEffect(() => {
    if (inputTrigger) {
      handleSend(null, inputTrigger)
    }
  }, [inputTrigger])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Simple Sentiment Analysis on query
  const detectSentiment = (text) => {
    const val = text.toLowerCase()
    if (val.includes('sad') || val.includes('unhappy') || val.includes('depressed') || val.includes('cry')) {
      setMood('sad')
      return 'sad'
    } else if (val.includes('happy') || val.includes('excited') || val.includes('great') || val.includes('awesome') || val.includes('yes')) {
      setMood('happy')
      return 'happy'
    } else if (val.includes('tired') || val.includes('sleepy') || val.includes('exhausted') || val.includes('dream')) {
      setMood('tired')
      return 'tired'
    } else if (val.includes('hype') || val.includes('motivate') || val.includes('celebrate') || val.includes('win')) {
      setMood('excited')
      return 'excited'
    }
    return 'default'
  }

  // Premium Backend Edge-TTS Streamer (High-fidelity female speech)
  const speakText = (text, voice) => {
    if (muteTextToSpeech) return

    // Cancel existing audio playback
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    try {
      // Fetch dynamic mp3 byte stream from Flask server tts route
      const ttsUrl = `/api/tts?text=${encodeURIComponent(text)}&voice=${voice}`
      const audio = new Audio(ttsUrl)
      audioRef.current = audio

      // Trigger pulsations of mouth and core when playing starts
      audio.onplay = () => {
        setMicActive(true)
      }
      audio.onended = () => {
        setMicActive(false)
      }
      audio.onerror = () => {
        setMicActive(false)
        fallbackSpeechSynthesis(text) // Fallback if server is busy/offline
      }

      audio.play().catch(e => {
        console.warn("Autoplay block or audio play fail, falling back to standard synthesis", e)
        fallbackSpeechSynthesis(text)
      })
    } catch (e) {
      fallbackSpeechSynthesis(text)
    }
  }

  // Fallback to HTML5 SpeechSynthesis (offline backup)
  const fallbackSpeechSynthesis = (text) => {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.95
    
    // Pick female speech profile
    const voices = window.speechSynthesis.getVoices()
    const femaleVoice = voices.find(v => v.name.includes('Zira') || v.name.includes('female') || v.name.includes('Google US English'))
    if (femaleVoice) utterance.voice = femaleVoice

    utterance.onstart = () => setMicActive(true)
    utterance.onend = () => setMicActive(false)
    window.speechSynthesis.speak(utterance)
  }

  // STT Voice Query Recognition
  const triggerVoiceRecog = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Web Speech API not supported in this browser.")
      return
    }

    const recog = new SpeechRecognition()
    recog.lang = 'en-US'
    recog.interimResults = false

    recog.onstart = () => {
      setVoiceActive(true)
      setMicActive(true)
    }

    recog.onresult = (event) => {
      const resultText = event.results[0][0].transcript
      handleSend(null, resultText)
    }

    recog.onerror = () => {
      setVoiceActive(false)
      setMicActive(false)
    }

    recog.onend = () => {
      setVoiceActive(false)
      setMicActive(false)
    }

    recog.start()
  }

  const handleSend = async (e, customQuery) => {
    if (e) e.preventDefault()
    const userMsg = customQuery || query
    if (!userMsg.trim()) return

    setMessages(prev => [...prev, { sender: 'user', text: userMsg, time: new Date() }])
    setQuery('')
    setLoading(true)

    const moodState = detectSentiment(userMsg)

    if (userMsg.toLowerCase().includes('enter hud mode') || userMsg.toLowerCase().includes('hologram')) {
      setHologramMode(true)
    }

    try {
      const res = await fetch(`/api/chat?message=${encodeURIComponent(userMsg)}`)
      const data = await res.json()
      
      let reply = data.reply || "Neural network returned empty mainframe reply."
      
      if (moodState === 'excited') {
        reply = "Splendid! " + reply
      } else if (moodState === 'sad') {
        reply = "I understand, Sir. " + reply
      }

      setMessages(prev => [...prev, { sender: 'jarvis', text: reply, time: new Date() }])
      speakText(reply, voiceProfile)
    } catch (err) {
      // Local client rules if server is busy/offline
      setTimeout(() => {
        let reply = "Standalone processor link active. Standing by, Sir."
        if (userMsg.toLowerCase().includes('hello') || userMsg.toLowerCase().includes('jarvis')) {
          reply = "Hello, Sir. I am JARVIS X Infinity. Standalone sub-core is operational."
        } else if (userMsg.toLowerCase().includes('focus')) {
          reply = "Acknowledged. Engaging focus parameters. Notifications are muted."
        }
        setMessages(prev => [...prev, { sender: 'jarvis', text: reply, time: new Date() }])
        speakText(reply, voiceProfile)
      }, 1000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative w-full h-full">
      {/* Boot Sequencer Overlay */}
      <AnimatePresence>
        {!appBooted && (
          <motion.div 
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/90 backdrop-blur-md rounded-lg border border-cyan-500/20 z-50 flex flex-col items-center justify-center gap-4"
          >
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 rounded-full border border-dashed border-cyan-400 flex items-center justify-center"
            >
              <Zap className="w-6 h-6 text-cyan-400" />
            </motion.div>
            <div className="text-center font-mono space-y-1">
              <h3 className="text-sm font-bold text-cyan-400 tracking-widest">JARVIS X INFINITY COGNITIVE CORE</h3>
              <p className="text-[10px] text-slate-500">ENGAGE SYSTEM AUDITS AND SPEECH LINKAGE</p>
            </div>
            <button 
              onClick={() => setAppBooted(true)}
              className="glow-button py-2 px-6 rounded text-xs font-bold font-mono tracking-widest"
            >
              BOOT CORE INTERFACE
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat HUD UI */}
      <div className="glass-panel w-full h-[320px] flex flex-col interactive">
        <div className="glass-panel-header">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>COGNITIVE CORE SYSTEM</span>
          </div>
          
          {/* Voice profile selectors */}
          <div className="flex items-center gap-3">
            <select 
              value={voiceProfile} 
              onChange={(e) => setVoiceProfile(e.target.value)}
              className="bg-black/40 border border-cyan-500/20 text-cyan-400 text-[10px] px-1.5 py-0.5 rounded focus:outline-none focus:border-cyan-500 font-mono cursor-pointer"
            >
              <option value="en-US-EmmaMultilingualNeural">VOICE: EMMA (FEMALE PREMIUM)</option>
              <option value="en-US-JennyNeural">VOICE: JENNY (NATURAL FEMALE)</option>
              <option value="hi-IN-SwaraNeural">VOICE: SWARA (HINDI FEMALE)</option>
            </select>
            <button 
              onClick={() => setMuteTextToSpeech(!muteTextToSpeech)}
              className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${muteTextToSpeech ? 'bg-red-500/20 text-red-400' : 'bg-cyan-500/20 text-cyan-400'}`}
            >
              {muteTextToSpeech ? 'MUTED' : 'SPEECH: ON'}
            </button>
          </div>
        </div>

        {/* Message Output Scroll Panel */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 scroll-smooth">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-2.5 text-xs font-mono ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.sender !== 'user' && (
                <div className="w-5 h-5 rounded border border-cyan-500/30 flex items-center justify-center bg-cyan-500/5">
                  <span className="text-[10px] text-cyan-400">J</span>
                </div>
              )}
              
              <div className={`max-w-[75%] p-2.5 rounded-lg border ${
                m.sender === 'user' 
                  ? 'bg-purple-500/10 border-purple-500/30 text-purple-200' 
                  : 'bg-cyan-500/5 border-cyan-500/20 text-cyan-100'
              }`}>
                <p className="text-[9px] text-slate-500 mb-1 flex items-center gap-1">
                  {m.sender === 'user' ? <User className="w-2.5 h-2.5" /> : <HelpCircle className="w-2.5 h-2.5" />}
                  {m.sender === 'user' ? 'USER' : 'JARVIS X'}
                </p>
                <p className="leading-relaxed">
                  {m.sender === 'jarvis' && idx === messages.length - 1 ? (
                    <TypewriterText text={m.text} speed={12} />
                  ) : m.text}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-2.5 text-xs font-mono justify-start">
              <div className="w-5 h-5 rounded border border-cyan-500/30 flex items-center justify-center bg-cyan-500/5 animate-spin">
                <RefreshCw className="w-3 h-3 text-cyan-400" />
              </div>
              <span className="text-cyan-400/60 self-center">PROCESSING SYNAPSES...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input query form */}
        <form onSubmit={handleSend} className="p-3 border-t border-slate-800 flex gap-2 bg-black/20">
          <button 
            type="button" 
            onClick={triggerVoiceRecog}
            className={`px-3 rounded border flex items-center justify-center transition-colors ${
              voiceActive 
                ? 'bg-red-500/20 border-red-500/60 text-red-400 animate-pulse' 
                : 'bg-black/30 border-slate-700 text-slate-400 hover:border-cyan-400 hover:text-cyan-400'
            }`}
          >
            {voiceActive ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter query commands or speak neural cues..." 
            className="flex-1 bg-black/40 border border-slate-700 rounded px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_8px_rgba(0,240,255,0.2)] font-mono"
          />

          <button type="submit" className="glow-button flex items-center justify-center px-4">
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  )
}

// Simple placeholder icon wrapper for loader
function Zap(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  )
}
