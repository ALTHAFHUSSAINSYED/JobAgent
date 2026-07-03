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
  CheckCircle,
  AlertCircle,
  Copy,
  Clock,
  HardDrive,
  Info
} from 'lucide-react'

function App() {
  const [data, setData] = useState(null)
  const [systemStats, setSystemStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [events, setEvents] = useState([])
  const [filterLevel, setFilterLevel] = useState('ALL')
  const [copiedHash, setCopiedHash] = useState('')
  const [socketsState, setSocketsState] = useState({
    logs: 'connecting',
    system: 'connecting',
    events: 'connecting'
  })
  
  const logsEndRef = useRef(null)

  // 1. Fetch initial snapshot
  const fetchDashboard = () => {
    fetch('/api/v1/dashboard')
      .then(res => res.json())
      .then(d => setData(d))
      .catch(e => console.error("Error loading dashboard data:", e))
  }

  useEffect(() => {
    fetchDashboard()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host

    // A. Logs Stream WebSocket
    const logsWs = new WebSocket(`${protocol}//${host}/api/v1/ws/logs`)
    logsWs.onopen = () => setSocketsState(prev => ({ ...prev, logs: 'connected' }))
    logsWs.onclose = () => setSocketsState(prev => ({ ...prev, logs: 'disconnected' }))
    logsWs.onmessage = (event) => {
      try {
        const logRecord = JSON.parse(event.data)
        setLogs(prev => [...prev, logRecord].slice(-250))
      } catch (e) {
        setLogs(prev => [...prev, {
          timestamp: new Date().toLocaleTimeString(),
          level: 'INFO',
          module: 'system',
          message: event.data
        }].slice(-250))
      }
    }

    // B. System Stats WebSocket (streams CPU, pool details and latencies)
    const systemWs = new WebSocket(`${protocol}//${host}/api/v1/ws/system`)
    systemWs.onopen = () => setSocketsState(prev => ({ ...prev, system: 'connected' }))
    systemWs.onclose = () => setSocketsState(prev => ({ ...prev, system: 'disconnected' }))
    systemWs.onmessage = (event) => {
      try {
        const stats = JSON.parse(event.data)
        setSystemStats(stats)
        // Auto-refresh configuration and metrics on statistics updates
        fetchDashboard()
      } catch (e) {
        console.error("Error parsing system stats:", e)
      }
    }

    // C. Events Alerts WebSocket
    const eventsWs = new WebSocket(`${protocol}//${host}/api/v1/ws/events`)
    eventsWs.onopen = () => setSocketsState(prev => ({ ...prev, events: 'connected' }))
    eventsWs.onclose = () => setSocketsState(prev => ({ ...prev, events: 'disconnected' }))
    eventsWs.onmessage = (event) => {
      try {
        const alertEvent = JSON.parse(event.data)
        setEvents(prev => [{
          id: Math.random().toString(36).substr(2, 9),
          time: new Date().toLocaleTimeString(),
          name: alertEvent.event,
          payload: alertEvent.payload
        }, ...prev].slice(0, 50))
      } catch (e) {
        console.error("Error parsing event bus alert:", e)
      }
    }

    return () => {
      logsWs.close()
      systemWs.close()
      eventsWs.close()
    }
  }, [])

  // Auto-scroll terminal
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopiedHash(text)
    setTimeout(() => setCopiedHash(''), 2000)
  }

  // Filter logs list based on user selections
  const filteredLogs = logs.filter(log => {
    if (filterLevel === 'ALL') return true
    return log.level === filterLevel
  })

  // Format bytes to KB
  const formatBytes = (bytes) => {
    if (!bytes) return "0 KB"
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  // Format epoch milliseconds or unix timestamp to local date
  const formatDate = (unixTimestamp) => {
    if (!unixTimestamp) return "N/A"
    return new Date(unixTimestamp * 1000).toLocaleString()
  }

  const { health, jobs_count, applications_count, resume_status, configuration, resumes, playwright_details } = data || {}
  const { system, latencies, database_pool } = systemStats || {}

  const getSocketStatusBadge = (state) => {
    if (state === 'connected') return <span className="text-[10px] bg-green-500/10 text-green-500 border border-green-500/30 px-2 py-0.5 rounded-full font-bold">ACTIVE</span>
    if (state === 'connecting') return <span className="text-[10px] bg-yellow-500/10 text-yellow-500 border border-yellow-500/30 px-2 py-0.5 rounded-full font-bold animate-pulse">CONNECTING</span>
    return <span className="text-[10px] bg-red-500/10 text-red-500 border border-red-500/30 px-2 py-0.5 rounded-full font-bold">DISCONNECTED</span>
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-200 font-sans selection:bg-blue-600 selection:text-white pb-10">
      
      {/* 1. Navbar Header */}
      <header className="border-b border-[#1f2937] bg-[#111827]/50 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg text-white shadow-md shadow-blue-500/20">
              <Cpu className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">JobPilot AI</h1>
              <p className="text-xs text-gray-500 font-medium">Autonomous Multi-Agent Recruiter</p>
            </div>
          </div>

          {/* Sockets Connection Status Panel */}
          <div className="flex flex-wrap items-center gap-3 text-xs bg-[#161b26] px-4 py-2 rounded-xl border border-gray-800">
            <div className="flex items-center gap-2 pr-3 border-r border-gray-800">
              <span className="text-gray-500 font-medium">Logs Socket:</span>
              {getSocketStatusBadge(socketsState.logs)}
            </div>
            <div className="flex items-center gap-2 pr-3 border-r border-gray-800">
              <span className="text-gray-500 font-medium">System Socket:</span>
              {getSocketStatusBadge(socketsState.system)}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500 font-medium">Events Socket:</span>
              {getSocketStatusBadge(socketsState.events)}
            </div>
          </div>
        </div>
      </header>

      {/* 2. Self Diagnosing Pillars Overview Grid */}
      <section className="max-w-7xl mx-auto px-6 mt-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          
          {/* PostgreSQL Component */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-4 flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-400 font-bold tracking-wider uppercase">PostgreSQL</span>
              <Database className="h-4 w-4 text-blue-500" />
            </div>
            <div>
              <span className="text-lg font-bold text-white block">
                {health?.database === 'healthy' ? "Online" : "Offline"}
              </span>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-2 pt-2 border-t border-gray-800/40">
                <span>Latency:</span>
                <span className="text-blue-400 font-semibold">{latencies?.database_ms !== -1 ? `${latencies?.database_ms || '0.0'} ms` : 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-1">
                <span>Pool Limits:</span>
                <span className="text-gray-300 font-medium">
                  {database_pool ? `${database_pool.active}/${database_pool.max}` : '0/0'}
                </span>
              </div>
            </div>
          </div>

          {/* Redis Event Broker */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-4 flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-400 font-bold tracking-wider uppercase">Redis Broker</span>
              <Layers className="h-4 w-4 text-orange-500" />
            </div>
            <div>
              <span className="text-lg font-bold text-white block">
                {health?.redis === 'healthy' ? "Connected" : "Offline"}
              </span>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-2 pt-2 border-t border-gray-800/40">
                <span>Latency:</span>
                <span className="text-orange-400 font-semibold">{latencies?.redis_ms !== -1 ? `${latencies?.redis_ms || '0.0'} ms` : 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-1">
                <span>Events Channels:</span>
                <span className="text-gray-300 font-medium">5 Subscribed</span>
              </div>
            </div>
          </div>

          {/* Playwright Browser */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-4 flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-400 font-bold tracking-wider uppercase">Playwright</span>
              <Globe className="h-4 w-4 text-purple-500" />
            </div>
            <div>
              <span className="text-lg font-bold text-white block">
                {playwright_details?.ready ? "Ready" : "Missing"}
              </span>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-2 pt-2 border-t border-gray-800/40">
                <span>Engine:</span>
                <span className="text-purple-400 font-semibold truncate max-w-[80px]">{playwright_details?.version || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-1">
                <span>Status:</span>
                <span className="text-gray-300 font-medium">{playwright_details?.installed ? 'Installed' : 'Missing'}</span>
              </div>
            </div>
          </div>

          {/* OpenRouter LLM */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-4 flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-400 font-bold tracking-wider uppercase">OpenRouter</span>
              <Key className="h-4 w-4 text-yellow-500" />
            </div>
            <div>
              <span className="text-lg font-bold text-white block">
                {latencies?.openrouter_ms !== -1.0 ? "Connected" : "Not Ready"}
              </span>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-2 pt-2 border-t border-gray-800/40">
                <span>Latency:</span>
                <span className="text-yellow-400 font-semibold">{latencies?.openrouter_ms !== -1.0 ? `${latencies?.openrouter_ms} ms` : 'Offline'}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-1">
                <span>API Key:</span>
                <span className="text-gray-300 font-medium">{latencies?.openrouter_ms !== -1.0 ? 'Valid' : 'Unset'}</span>
              </div>
            </div>
          </div>

          {/* Configuration Engine */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-4 flex flex-col justify-between shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-400 font-bold tracking-wider uppercase">Config Watcher</span>
              <Settings className="h-4 w-4 text-green-500" />
            </div>
            <div>
              <span className="text-lg font-bold text-white block">
                {health?.configuration === 'healthy' ? "Synchronized" : "Out of sync"}
              </span>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-2 pt-2 border-t border-gray-800/40">
                <span>Hot Reload:</span>
                <span className="text-green-400 font-semibold">Active</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-gray-500 mt-1">
                <span>Change Detector:</span>
                <span className="text-gray-300 font-medium">Auto Watch</span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 3. Main Dashboard Content Grid */}
      <main className="max-w-7xl mx-auto px-6 mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Configuration Snapshot & Events Logs */}
        <section className="lg:col-span-1 flex flex-col gap-6">
          
          {/* Card A: Candidate Profile Details */}
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
                <span className="font-semibold text-white">{configuration?.expected_ctc || 'N/A'} LPA</span>
              </div>
              <div className="flex justify-between border-b border-gray-800/40 pb-2">
                <span className="text-gray-500 font-medium">Total Experience</span>
                <span className="font-semibold text-white">
                  {configuration?.experience_years ? `${configuration.experience_years.toFixed(2)} Years` : '0.00 Years'}
                </span>
              </div>
              <div className="flex justify-between border-b border-gray-800/40 pb-2">
                <span className="text-gray-500 font-medium">Immediate Joiner</span>
                <span className="font-semibold text-white">{configuration?.immediate_joiner ? "Yes" : "No"}</span>
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

          {/* Card B: Real-Time Event Bus Notifications Alert */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm flex flex-col flex-grow">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-orange-500" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">Event Bus alerts</h2>
              </div>
              <span className="text-xs bg-orange-500/10 text-orange-400 font-semibold px-2.5 py-0.5 rounded-full border border-orange-500/20">PubSub</span>
            </div>

            <div className="flex-grow overflow-y-auto max-h-[280px] custom-scrollbar flex flex-col gap-2.5 pr-1">
              {events.length === 0 ? (
                <div className="text-gray-600 text-xs italic text-center py-6">
                  No event notifications captured yet. Try modifying profile.yaml.
                </div>
              ) : (
                events.map(ev => (
                  <div key={ev.id} className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-mono text-orange-400 font-bold">[{ev.name}]</span>
                      <span className="text-gray-600 font-medium">{ev.time}</span>
                    </div>
                    <pre className="text-gray-400 overflow-x-auto text-[10px] bg-[#070b13] p-1.5 rounded border border-gray-900/40">
                      {JSON.stringify(ev.payload, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* RIGHT COLUMN (2 columns wide): System Monitor, Resumes & Terminal */}
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
                <FileText className="h-6 w-6" />
              </div>
              <div>
                <span className="text-xs text-gray-500 block font-medium">Scanned Resumes</span>
                <span className="text-2xl font-bold text-white">{resumes?.length || 0}</span>
              </div>
            </div>
          </div>

          {/* Card D: Scanned Resumes Directory Details */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 border-b border-gray-800 pb-3 mb-4">
              <HardDrive className="h-5 w-5 text-purple-500" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Workspace Resumes Registry</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left text-gray-400">
                <thead className="bg-[#1f2937]/30 text-gray-500 uppercase text-[10px] tracking-wider font-semibold border-b border-gray-800">
                  <tr>
                    <th className="py-2.5 px-3">File Name</th>
                    <th className="py-2.5 px-3">Classification</th>
                    <th className="py-2.5 px-3">Size</th>
                    <th className="py-2.5 px-3">Last Modified</th>
                    <th className="py-2.5 px-3 text-right">SHA-256 Hash</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/40">
                  {resumes && resumes.length > 0 ? (
                    resumes.map((res, idx) => (
                      <tr key={idx} className="hover:bg-gray-800/20 transition-colors">
                        <td className="py-3 px-3 font-medium text-white">{res.filename}</td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${res.type === 'Portfolio Resume' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-purple-500/10 text-purple-400 border-purple-500/20'}`}>
                            {res.type}
                          </span>
                        </td>
                        <td className="py-3 px-3">{formatBytes(res.size_bytes)}</td>
                        <td className="py-3 px-3 text-gray-500">{formatDate(res.last_modified)}</td>
                        <td className="py-3 px-3 text-right font-mono">
                          <div className="flex items-center justify-end gap-1.5">
                            <span className="text-[10px] text-gray-500 max-w-[90px] truncate" title={res.sha256}>
                              {res.sha256}
                            </span>
                            <button 
                              onClick={() => copyToClipboard(res.sha256)}
                              className="text-gray-500 hover:text-white transition-colors"
                              title="Copy full hash"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                            {copiedHash === res.sha256 && (
                              <span className="text-[9px] bg-green-500/20 text-green-400 px-1 rounded border border-green-500/30">Copied</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="py-6 text-center text-gray-600 italic">
                        No resumes (PDF/DOCX) scanned in resumes/ folder yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Card E: Structured Log Stream Terminal */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl shadow-md overflow-hidden flex flex-col flex-grow min-h-[300px]">
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
            <div className="bg-[#090d16] p-4 font-mono text-xs overflow-y-auto flex-grow h-[300px] custom-scrollbar flex flex-col gap-1.5">
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

          {/* Card F: Detailed System spec info */}
          <div className="bg-[#161b26] border border-[#1f2937] rounded-xl p-5 shadow-sm text-xs">
            <div className="flex items-center gap-2 border-b border-gray-800 pb-3 mb-4">
              <Cpu className="h-5 w-5 text-purple-500" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">System Specifications</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Python Engine</span>
                <span className="text-white font-semibold">{system?.python_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">PostgreSQL Engine</span>
                <span className="text-white font-semibold truncate block">{system?.postgres_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Redis Broker</span>
                <span className="text-white font-semibold">{system?.redis_version || 'Loading...'}</span>
              </div>
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800">
                <span className="text-gray-500 block font-medium">Vite Bundle Host</span>
                <span className="text-white font-semibold">{system?.docker_status === 'healthy' ? 'Docker Sandbox' : 'Local Host'}</span>
              </div>
            </div>

            <div className="bg-[#0b0f19] p-3 rounded-lg border border-gray-800 mt-4 font-mono text-[10px]">
              <div className="flex flex-col md:flex-row justify-between gap-1.5">
                <div className="flex gap-2">
                  <span className="text-purple-400">Playwright Chromium Binary:</span>
                  <span className="text-gray-300 break-all">{playwright_details?.executable_path || 'N/A'}</span>
                </div>
                <div className="flex gap-2 min-w-[120px] justify-end">
                  <span className="text-purple-400">Ready:</span>
                  <span className={playwright_details?.ready ? "text-green-400" : "text-red-400"}>
                    {playwright_details?.ready ? "PASS" : "FAIL"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* 4. Footer */}
      <footer className="max-w-7xl mx-auto px-6 mt-10 pt-6 border-t border-[#1f2937] flex flex-col md:flex-row items-center justify-between text-xs text-gray-600 gap-4">
        <div className="flex items-center gap-3">
          <GitBranch className="h-4 w-4" />
          <span>Active Branch: <strong className="text-gray-400 font-semibold">{system?.git_branch || 'sprint-1.4'}</strong></span>
          <span className="text-gray-800">|</span>
          <span>Commit Hash: <strong className="text-gray-400 font-semibold">{system?.git_commit || 'N/A'}</strong></span>
        </div>
        <div>
          <span>Platform Version: <strong className="text-gray-400 font-semibold">0.4.0 (Sprint 1.4 Release)</strong></span>
        </div>
      </footer>

    </div>
  )
}

export default App
