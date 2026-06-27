import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Mic, MicOff, Volume2, User, HelpCircle, Terminal } from 'lucide-react'

// Custom Typewriter text animation component
function TypewriterText({ text, speed = 20 }) {
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

export default function ChatHUD({ setMood, setMicActive, setHologramMode, inputTrigger }) {
  const [messages, setMessages] = useState([
    { sender: 'jarvis', text: "Hello, Sir. I am JARVIS X. System interface online. Stand by for voice query linkage.", time: new Date() }
  ])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [voiceActive, setVoiceActive] = useState(false)
  const [voiceMode, setVoiceMode] = useState('assistant') // professional, friendly, motivational, assistant
  const [muteTextToSpeech, setMuteTextToSpeech] = useState(false)

  const chatEndRef = useRef(null)

  // Listen for screen vision/external triggers
  useEffect(() => {
    if (inputTrigger) {
      handleSend(null, inputTrigger)
    }
  }, [inputTrigger])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Simple Sentiment Analysis on query to alter avatar colors
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

  // HTML5 Web Speech Synthesis (TTS) Response
  const speakText = (text, mode) => {
    if (muteTextToSpeech) return
    window.speechSynthesis.cancel() // Stop prior voice queues

    const utterance = new SpeechSynthesisUtterance(text)
    
    // Configure voice properties based on Voice Mode
    switch (mode) {
      case 'professional':
        utterance.rate = 1.05
        utterance.pitch = 0.95
        break;
      case 'friendly':
        utterance.rate = 1.0
        utterance.pitch = 1.15
        break;
      case 'motivational':
        utterance.rate = 1.15
        utterance.pitch = 1.05
        break;
      case 'assistant':
      default:
        utterance.rate = 0.95
        utterance.pitch = 1.0
        break;
    }

    // Attempt to pick a premium English/male voice if available
    const voices = window.speechSynthesis.getVoices()
    const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Natural'))
    if (preferredVoice) {
      utterance.voice = preferredVoice
    }

    utterance.onstart = () => setMicActive(true) // Pulsate avatar mouth during speak
    utterance.onend = () => setMicActive(false)
    utterance.onerror = () => setMicActive(false)

    window.speechSynthesis.speak(utterance)
  }

  // Speech-to-Text mock (or html5 web SpeechRecognition)
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

    recog.onerror = (e) => {
      console.error(e)
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

    // Log message
    setMessages(prev => [...prev, { sender: 'user', text: userMsg, time: new Date() }])
    setQuery('')
    setLoading(true)

    // Sentiment check
    const moodState = detectSentiment(userMsg)

    // Hologram activation commands
    if (userMsg.toLowerCase().includes('enter hud mode') || userMsg.toLowerCase().includes('hologram')) {
      setHologramMode(true)
    }

    // Call local Flask API chat proxy
    try {
      const res = await fetch(`/api/chat?message=${encodeURIComponent(userMsg)}`)
      const data = await res.json()
      
      let reply = data.reply || "Connection check: API online but returned empty reply frame."
      
      // Inject mood styling prefixes to speech
      if (moodState === 'excited') {
        reply = "Sensational! " + reply
      } else if (moodState === 'sad') {
        reply = "I understand, Sir. Let us focus. " + reply
      }

      setMessages(prev => [...prev, { sender: 'jarvis', text: reply, time: new Date() }])
      speakText(reply, voiceMode)
    } catch (err) {
      console.warn("Flask link failed. Bypassing to local client-side rule compiler.", err)
      
      // Fallback client answers if backend is offline
      setTimeout(() => {
        let reply = "Standalone processor link active. Standing by, Sir."
        if (userMsg.toLowerCase().includes('hello') || userMsg.toLowerCase().includes('jarvis')) {
          reply = "Hello, Sir. I am JARVIS X. Standalone sub-core is operational. How may I assist you today?"
        } else if (userMsg.toLowerCase().includes('focus')) {
          reply = "Acknowledged. Engaging focus parameters. Notifications are muted, launching lofi audio waves."
        } else if (userMsg.toLowerCase().includes('help')) {
          reply = "Command matrix supports time syncs, weather readings, Pomodoro timers, and speech feedback loops."
        }
        setMessages(prev => [...prev, { sender: 'jarvis', text: reply, time: new Date() }])
        speakText(reply, voiceMode)
      }, 1000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div 
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="glass-panel w-full h-[320px] flex flex-col interactive"
    >
      {/* HUD Controller Headings */}
      <div className="glass-panel-header">
        <span><Terminal className="inline w-4 h-4 mr-2" />COGNITIVE CORE SYSTEM</span>
        
        {/* Voice Mode Selector */}
        <div className="flex items-center gap-3">
          <select 
            value={voiceMode} 
            onChange={(e) => setVoiceMode(e.target.value)}
            className="bg-black/40 border border-cyan-500/20 text-cyan-400 text-[10px] px-1.5 py-0.5 rounded focus:outline-none focus:border-cyan-500 font-mono cursor-pointer"
          >
            <option value="assistant">VOICE: ASSISTANT</option>
            <option value="professional">VOICE: PROFESSIONAL</option>
            <option value="friendly">VOICE: FRIENDLY</option>
            <option value="motivational">VOICE: HYPE MODE</option>
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
    </motion.div>
  )
}
