import React, { useState, useRef, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Menu, Shield, Activity, Users, Settings, Target, X, Move } from 'lucide-react';
import { create } from 'zustand';

const useStore = create((set) => ({
  activeTab: 'dashboard',
  agentRole: 'surveillance',
  protectedCameras: [],
  activeIncidents: [],
  setActiveTab: (tab) => set({ activeTab: tab }),
  setAgentRole: (role) => set({ agentRole: role }),
  addProtectedCamera: (camera) => set((state) => ({ protectedCameras: [...state.protectedCameras, camera] })),
  removeProtectedCamera: (camera) => set((state) => ({ protectedCameras: state.protectedCameras.filter(c => c !== camera) })),
  addActiveIncident: (incident) => set((state) => ({ activeIncidents: [...state.activeIncidents, incident] })),
  removeActiveIncident: (incident) => set((state) => ({ activeIncidents: state.activeIncidents.filter(i => i !== incident) }))
}));

const ConstellationGraph = () => {
  const nodes = [
    { id: 'cam21', type: 'camera', label: 'CAM_21_PTZ', x: 150, y: 150 },
    { id: 'cam15', type: 'camera', label: 'CAM_15_FIXED', x: 450, y: 100 },
    { id: 'obs1', type: 'observation', label: 'Subject Spotted', x: 250, y: 220, quality: 'high' },
    { id: 'obs2', type: 'observation', label: 'Badge Denied', x: 380, y: 300, quality: 'low' },
    { id: 'zoneA', type: 'zone', label: 'Executive Wing', x: 600, y: 250 }
  ];

  const links = [
    { source: 'cam21', target: 'obs1', type: 'sightline' },
    { source: 'obs1', target: 'obs2', type: 'sequence' },
    { source: 'cam15', target: 'obs2', type: 'sightline' },
    { source: 'obs2', target: 'zoneA', type: 'movement' }
  ];

  const getNodeColor = (node) => {
    if (node.type === 'camera') return '#0ea5e9'; // Tailwind sky-500
    if (node.type === 'zone') return '#64748b'; // Tailwind slate-500
    return node.quality === 'high' ? '#22c55e' : '#eab308'; // green-500 vs yellow-500
  };

  return (
    <div className="w-full h-[500px] bg-gray-900/50 rounded-xl border border-gray-800 relative overflow-hidden flex items-center justify-center shadow-inner">
      <svg className="w-full h-full absolute inset-0">
        {/* Draw Links first so they appear under nodes */}
        {links.map(link => {
          const src = nodes.find(n => n.id === link.source);
          const tgt = nodes.find(n => n.id === link.target);
          return (
            <line
              key={`${link.source}-${link.target}`}
              x1={src.x} y1={src.y}
              x2={tgt.x} y2={tgt.y}
              stroke={link.type === 'sequence' ? '#f43f5e' : '#334155'}
              strokeWidth={link.type === 'sequence' ? '3' : '2'}
              strokeDasharray={link.type === 'sightline' ? '5,5' : 'none'}
              className="opacity-70"
            />
          );
        })}
        
        {/* Draw Nodes */}
        {nodes.map(node => (
          <g key={node.id} className="cursor-pointer hover:opacity-80 transition-opacity">
            {/* Outer Glow for Observations */}
            {node.type === 'observation' && (
              <circle cx={node.x} cy={node.y} r="24" fill={getNodeColor(node)} className="opacity-20 animate-pulse" />
            )}
            <circle cx={node.x} cy={node.y} r={node.type === 'zone' ? '30' : '16'} fill={getNodeColor(node)} stroke="#0f172a" strokeWidth="3" />
            
            {/* Node Labels */}
            <text x={node.x} y={node.y + (node.type === 'zone' ? 45 : 30)} textAnchor="middle" fill="#cbd5e1" fontSize="12" fontWeight="600" className="drop-shadow-md">
              {node.label}
            </text>
          </g>
        ))}
      </svg>
      <div className="absolute top-4 left-4 bg-black/60 px-3 py-2 rounded border border-gray-800 text-xs text-gray-400">
        <div className="flex items-center gap-2 mb-1"><span className="w-3 h-3 rounded-full bg-sky-500"></span> Camera Source</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-3 h-3 rounded-full bg-green-500"></span> High-Quality Evidence</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> Partial/Low-Quality Evidence</div>
        <div className="flex items-center gap-2"><span className="w-8 h-0.5 bg-rose-500"></span> Temporal Sequence</div>
      </div>
    </div>
  );
};

const DraggablePiP = ({ title, cameraName, timestamp, onClose }) => {
  const [position, setPosition] = useState({ x: 100, y: 100 });
  const [isDragging, setIsDragging] = useState(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - dragOffset.current.x,
        y: e.clientY - dragOffset.current.y
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
  };

  return (
    <div
      className={`absolute z-50 bg-[#1e1e1e]/80 backdrop-blur-md border border-gray-700/50 rounded-xl shadow-2xl flex flex-col overflow-hidden w-80 transition-shadow ${isDragging ? 'shadow-accent/20 cursor-grabbing' : 'cursor-grab'}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`
      }}
    >
      <div 
        className="flex justify-between items-center bg-gray-900/80 p-2 border-b border-gray-700/50 select-none"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2 text-gray-300 font-semibold text-sm">
          <Move size={14} className="text-gray-500" />
          {title}
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          <X size={16} />
        </button>
      </div>
      <div className="relative bg-black aspect-video flex items-center justify-center">
        {/* Placeholder for actual video feed */}
        <div className="text-gray-700 font-mono text-xs text-center">
          <div>FEED OFFLINE</div>
          <div className="mt-1 opacity-50">{cameraName}</div>
        </div>
        <div className="absolute bottom-2 right-2 text-[10px] font-mono text-red-500 bg-black/50 px-1 rounded">
          {timestamp}
        </div>
        <div className="absolute top-2 left-2 text-[10px] font-mono text-white bg-red-600 px-1 rounded font-bold animate-pulse">
          REC
        </div>
      </div>
    </div>
  );
};
  const { setActiveTab, activeTab } = useStore();

  const getTabClass = (tab) => {
    return `flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-800 transition-colors ${activeTab === tab ? 'text-accent border-l-2 border-accent bg-gray-800' : 'text-gray-400'}`;
  };

  return (
    <div className="bg-brand w-64 border-r border-gray-800 h-full flex flex-col">
      <div className="p-4 border-b border-gray-800 font-bold text-accent text-lg flex items-center gap-2">
        <Shield size={20} />
        SafeTask AI
      </div>
      <nav className="flex-1 overflow-y-auto mt-4">
        <ul>
          <li className={getTabClass('dashboard')} onClick={() => setActiveTab('dashboard')}>
            <Activity size={18} />
            Dashboard
          </li>
          <li className={getTabClass('security')} onClick={() => setActiveTab('security')}>
            <Target size={18} />
            Command Center
          </li>
          <li className={getTabClass('activity')} onClick={() => setActiveTab('activity')}>
            <Menu size={18} />
            Review Deck
          </li>
          <li className={getTabClass('users')} onClick={() => setActiveTab('users')}>
            <Users size={18} />
            Subject Profiles
          </li>
          <li className={getTabClass('settings')} onClick={() => setActiveTab('settings')}>
            <Settings size={18} />
            Settings
          </li>
        </ul>
      </nav>
    </div>
  );
};

const TopNavigation = () => {
  const { agentRole, activeIncidents } = useStore();
  
  return (
    <header className="bg-brand border-b border-gray-800 p-4 text-gray-200 flex justify-between items-center">
      <div className="font-semibold text-lg text-gray-300">Surveillance Operations</div>
      <div className="flex gap-4 items-center">
        <div className="bg-red-900/20 text-red-400 border border-red-900/50 px-3 py-1 rounded text-xs font-bold">
          {activeIncidents.length} ACTIVE INCIDENTS
        </div>
        <div className="flex items-center gap-2 bg-gray-800 px-3 py-1 rounded">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-xs uppercase">{agentRole} AGENT</span>
        </div>
      </div>
    </header>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-900 text-gray-200 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <TopNavigation />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
};

const App = () => {
  const { activeTab } = useStore();
  const [pips, setPips] = React.useState([]);

  const spawnPip = () => {
    setPips([...pips, {
      id: Date.now(),
      title: `Review: CAM_${Math.floor(Math.random()*100)}`,
      cameraName: 'Casino Floor PTZ',
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const closePip = (id) => {
    setPips(pips.filter(p => p.id !== id));
  };

  return (
    <Layout>
      <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
        {activeTab === 'dashboard' && <div>Active View: DASHBOARD</div>}
        
        {activeTab === 'security' && (
          <div className="w-full h-full flex flex-col">
            <h2 className="text-xl font-bold text-gray-200 mb-4">Constellation Review</h2>
            <ConstellationGraph />
          </div>
        )}

        {activeTab === 'activity' && (
          <>
            <div>Active View: REVIEW DECK</div>
            <button 
              onClick={spawnPip}
              className="bg-accent/20 text-accent border border-accent/50 px-4 py-2 rounded shadow hover:bg-accent/30 transition-colors"
            >
              Spawn Review PiP
            </button>
          </>
        )}
        
        {['users', 'settings'].includes(activeTab) && (
          <div>Active View: {activeTab.toUpperCase()}</div>
        )}
      </div>
      
      {/* Render Floating PiPs */}
      {pips.map((pip, idx) => (
        <DraggablePiP 
          key={pip.id} 
          title={pip.title} 
          cameraName={pip.cameraName} 
          timestamp={pip.timestamp} 
          onClose={() => closePip(pip.id)} 
        />
      ))}
    </Layout>
  );
};

const root = createRoot(document.getElementById('root'));
root.render(<App />);