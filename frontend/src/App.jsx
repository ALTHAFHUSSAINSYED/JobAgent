import React, { useEffect, useState, useRef } from 'react'
import { 
  Activity, 
  Database, 
  Layers, 
  Globe, 
  Key, 
  Terminal, 
  Briefcase, 
  FileText, 
  Compass, 
  RefreshCw, 
  Settings, 
  Cpu, 
  GitBranch, 
  HelpCircle,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

function App() {
  const [data, setData] = useState(null)
  const [systemInfo, setSystemInfo] = useState(null)
  const [logs, setLogs] = useState([])
  const [filterLevel, setFilterLevel] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const logsEndRef = useRef(null)

  // 1. Fetch unified dashboard metrics
  const fetchDashboard = () => {
    fetch('/api/v1/dashboard')
      .then(res => res.json())
      .then(d => {
        setData(d)
        setLoading(false)
      })
      .catch(e => console.error("Error loading dashboard data:", e))
  }

  // 2. Fetch system dependencies
  const fetchSystemInfo = () => {
    fetch('/api/v1/system/info')
      .then(res => res.json())
      .then(d => setSystemInfo(d))
      .catch(e => console.error("Error loading system details:", e))
  }

  useEffect(() => {
    fetchDashboard()
    fetchSystemInfo()

    // 3. Connect to logs streaming socket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/logs`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      try {
        const logRecord = JSON.parse(event.data)
        setLogs(prev => [...prev, logRecord].slice(-200)) // retain last 200 logs
      } catch (e) {
        // Fallback for non-JSON logs
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          level: 'INFO',
          module: 'system',
          message: event.data
        }].slice(-200))
      }
    }

    ws.onerror = (e) => console.error("WebSocket log stream error:", e)

    return () => {
      ws.close()
    }
  }, [])

  // Auto-scroll terminal
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#0b0f19] text-gray-400">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="h-10 w-10 animate-spin text-blue-500" />
          <p className="text-sm font-medium tracking-wide">Initializing Orchestrator Dashboard...</p>
        </div>
      </div>
    )
  }

  const { health, jobs_count, applications_count, resume_status, configuration } = data || {}

  // Filter logs list based on user selections
  const filteredLogs = logs.filter(log => {
    if (filterLevel === 'ALL') return true
    return log.level === filterLevel
  })

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-200 font-sans selection:bg-blue-600 selection:text-white pb-10">
      
      {/* 1. Navbar Header */}
      <header className="border-b border-[#1f2937] bg-[#111827]/50 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg text-white shadow-md shadow-blue-500/20">
              <Cpu className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">JobPilot AI</h1>
              <p className="text-xs text-gray-500 font-medium">Autonomous Multi-Agent Recruiter</p>
            </div>
          </div>

          {/* Quick Pillar Status Badges */}
          <div className="hidden md:flex items-center gap-4 text-xs font-semibold">
            <span className="text-gray-500">PILLARS:</span>
            <div className="flex items-center gap-2 bg-[#161b26] px-3 py-1.5 rounded-full border border-gray-800">
              <Database className="h-3.5 w-3.5 text-blue-500" />
              <span>DB:</span>
              <span className={health?.database === 'healthy' ? "text-green-500" : "text-red-500"}>
                {health?.database === 'healthy' ? "🟢 Online" : "🔴 Offline"}
              </span>
            </div>
            <div className="flex items-center gap-2 bg-[#161b26] px-3 py-1.5 rounded-full border border-gray-800">
              <Layers className="h-3.5 w-3.5 text-orange-500" />
              <span>Redis:</span>
              <span className={health?.redis === 'healthy' ? "text-green-500" : "text-red-500"}>
                {health?.redis === 'healthy' ? "🟢 Online" : "🔴 Offline"}
              </span>
            </div>
            <div className="flex items-center gap-2 bg-[#161b26] px-3 py-1.5 rounded-full border border-gray-800">
              <Globe className="h-3.5 w-3.5 text-purple-500" />
              <span>Browser:</span>
              <span className={health?.playwright === 'healthy' ? "text-green-500" : "text-red-500"}>
                {health?.playwright === 'healthy' ? "🟢 Ready" : "🔴 Missing"}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Main Dashboard Content Grid */}
      <main className="max-w-7xl mx-auto px-6 mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Configuration Snapshot */}
        <section className="lg:col-span-1 flex flex-col gap-6">
          
          {/* Card A: Config Profiles summary */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-blue-500" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">Candidate Profile</h2>
              </div>
              <span className="text-xs bg-green-500/10 text-green-500 font-medium px-2 py-0.5 rounded-full border border-green-500/20">Active</span>
            </div>

            <div className="flex flex-col gap-4 text-sm">
              <div className="flex justify-between border-b border-gray-800/40 pb-2">
                <span className="text-gray-500 font-medium">Expected CTC</span>
                <span className="font-semibold text-white">{configuration?.expected_ctc || 'N/A'}</span>
              </div>
              <div className="flex justify-between border-b border-gray-800/40 pb-2">
                <span className="text-gray-500 font-medium">Total Experience</span>
                <span className="font-semibold text-white">{configuration?.experience_years} Years</span>
              </div>
              <div className="flex justify-between border-b border-gray-800/40 pb-2">
                <span className="text-gray-500 font-medium">Immediate Joiner</span>
                <span className="font-semibold text-white">{configuration?.immediate_joiner ? "✅ Yes" : "❌ No"}</span>
              </div>
              <div className="flex flex-col gap-2">
                <span className="text-gray-500 font-medium">Preferred Locations</span>
                <div className="flex flex-wrap gap-1.5">
                  {configuration?.preferred_locations.map((loc, idx) => (
                    <span key={idx} className="bg-gray-800 text-xs px-2.5 py-1 rounded-md text-gray-300 font-semibold border border-gray-700">
                      {loc}
                    </span>
                  )) || <span className="text-gray-500">None</span>}
                </div>
              </div>
              <div className="flex flex-col gap-2 pt-2">
                <div className="flex justify-between items-center">
                  <span className="text-gray-500 font-medium">Verified Skills</span>
                  <span className="text-xs bg-blue-500/10 text-blue-400 font-semibold px-2 py-0.5 rounded-full border border-blue-500/25">
                    {configuration?.skills_count} Total
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5 max-h-[140px] overflow-y-auto custom-scrollbar pr-1">
                  {configuration?.skills_list.map((skill, idx) => (
                    <span key={idx} className="bg-[#1c2333] text-xs px-2.5 py-1 rounded-md text-blue-300 border border-blue-900/30">
                      {skill}
                    </span>
                  )) || <span className="text-gray-500">None</span>}
                </div>
              </div>
            </div>
          </div>

          {/* Card B: Resume Intelligence */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-orange-500" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">Resume Intelligence</h2>
              </div>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${resume_status?.loaded ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'}`}>
                {resume_status?.loaded ? 'Loaded' : 'Missing'}
              </span>
            </div>

            <div className="flex flex-col gap-3 text-sm">
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-xs text-gray-500 block font-medium mb-1">CURRENT ACTIVE ATTACHMENT</span>
                <span className="font-mono text-xs text-orange-300 truncate block">
                  {resume_status?.version || 'No resume file detected'}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs mt-1">
                <span className="text-gray-500">Developer Profile:</span>
                <a href={resume_status?.portfolio} target="_blank" rel="noreferrer" className="text-blue-500 font-semibold hover:underline">
                  Portfolio Link &rarr;
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* RIGHT COLUMN (2 columns wide): System Monitor, Logs & Metrics */}
        <section className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Card C: Metrics Overview Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 flex items-center gap-4">
              <div className="bg-blue-600/10 border border-blue-500/20 p-3 rounded-lg text-blue-500">
                <Briefcase className="h-6 w-6" />
              </div>
              <div>
                <span className="text-xs text-gray-500 block font-medium">Scraped Jobs</span>
                <span className="text-2xl font-bold text-white">{jobs_count}</span>
              </div>
            </div>
            <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 flex items-center gap-4">
              <div className="bg-green-600/10 border border-green-500/20 p-3 rounded-lg text-green-500">
                <Compass className="h-6 w-6" />
              </div>
              <div>
                <span className="text-xs text-gray-500 block font-medium">Applications Filed</span>
                <span className="text-2xl font-bold text-white">{applications_count}</span>
              </div>
            </div>
            <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 flex items-center gap-4">
              <div className="bg-purple-600/10 border border-purple-500/20 p-3 rounded-lg text-purple-500">
                <Activity className="h-6 w-6" />
              </div>
              <div>
                <span className="text-xs text-gray-500 block font-medium">Platform Health</span>
                <span className={`text-sm font-extrabold uppercase px-2.5 py-0.5 rounded-full border ${health?.status === 'healthy' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'}`}>
                  {health?.status === 'healthy' ? 'PASS' : 'FAIL'}
                </span>
              </div>
            </div>
          </div>

          {/* Card D: Structured Log Stream Terminal */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl shadow-md overflow-hidden flex flex-col flex-grow min-h-[350px]">
            <div className="bg-[#1c2333] px-5 py-3 border-b border-gray-800 flex flex-col md:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <Terminal className="h-4.5 w-4.5 text-blue-500" />
                <h3 className="text-sm font-bold text-white tracking-wide uppercase">Real-Time Diagnostics Console</h3>
              </div>
              
              {/* Level Filters */}
              <div className="flex items-center gap-2 text-xs font-semibold">
                <span className="text-gray-500">LEVEL:</span>
                {['ALL', 'INFO', 'WARNING', 'ERROR'].map(lvl => (
                  <button 
                    key={lvl}
                    onClick={() => setFilterLevel(lvl)}
                    className={`px-3 py-1 rounded transition-colors ${filterLevel === lvl ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                  >
                    {lvl}
                  </button>
                ))}
                <button 
                  onClick={() => setLogs([])}
                  className="bg-red-950/40 text-red-400 border border-red-900/30 px-3 py-1 rounded hover:bg-red-900/20 ml-2"
                >
                  Clear Console
                </button>
              </div>
            </div>

            {/* Terminal Body */}
            <div className="bg-[#090d16] p-4 font-mono text-xs overflow-y-auto flex-grow h-[350px] custom-scrollbar flex flex-col gap-1.5">
              {filteredLogs.length === 0 ? (
                <div className="text-gray-600 italic h-full flex items-center justify-center">
                  Waiting for system event updates...
                </div>
              ) : (
                filteredLogs.map((log, idx) => {
                  let lvlColor = 'text-green-400'
                  if (log.level === 'WARNING') lvlColor = 'text-yellow-500 font-medium'
                  if (log.level === 'ERROR') lvlColor = 'text-red-500 font-bold'
                  
                  return (
                    <div key={idx} className="flex gap-2 border-b border-gray-900/20 pb-1 hover:bg-gray-900/10">
                      <span className="text-gray-600">[{log.timestamp}]</span>
                      <span className={`w-14 uppercase tracking-wider ${lvlColor}`}>[{log.level}]</span>
                      <span className="text-blue-400">[{log.module}]</span>
                      <span className="text-gray-300 flex-grow break-all">{log.message}</span>
                    </div>
                  )
                })
              )}
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* Card E: System info */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 border-b border-gray-800 pb-3 mb-4">
              <Cpu className="h-5 w-5 text-purple-500" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">System Information</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Python Engine</span>
                <span className="text-white font-semibold">{systemInfo?.python_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">PostgreSQL Server</span>
                <span className="text-white font-semibold truncate block">{systemInfo?.postgres_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Redis Broker</span>
                <span className="text-white font-semibold">{systemInfo?.redis_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Playwright Version</span>
                <span className="text-white font-semibold">{systemInfo?.playwright_version || 'Loading...'}</span>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* 3. Footer */}
      <footer className="max-w-7xl mx-auto px-6 mt-10 pt-6 border-t border-[#1f2937] flex flex-col md:flex-row items-center justify-between text-xs text-gray-600 gap-4">
        <div className="flex items-center gap-3">
          <GitBranch className="h-4 w-4" />
          <span>Active Branch: <strong className="text-gray-400 font-semibold">{systemInfo?.git_branch || 'sprint-1.3'}</strong></span>
          <span className="text-gray-800">|</span>
          <span>Commit Hash: <strong className="text-gray-400 font-semibold">{systemInfo?.git_commit || 'N/A'}</strong></span>
        </div>
        <div>
          <span>Platform Version: <strong className="text-gray-400 font-semibold">0.3.0</strong></span>
        </div>
      </footer>

    </div>
  )
}

export default App
