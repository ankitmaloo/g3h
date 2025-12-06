import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import CreationScreen from "./screens/CreationScreen";
import DetectionScreen from "./screens/DetectionScreen";
import { Button } from "@/components/ui/button";

function App() {
  useEffect(() => {
    // Force dark mode for the elite agency look
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-zinc-950 text-white font-sans overflow-hidden flex flex-col">
        {/* Navigation Header */}
        <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-zinc-950/80 backdrop-blur-md border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(249,115,22,0.5)]" />
            <span className="font-bold tracking-tight text-lg">NEXUS<span className="font-light text-zinc-400">PORTRAIT</span></span>
          </div>

          <nav className="flex items-center gap-1 bg-zinc-900/50 p-1 rounded-full border border-white/5">
            <NavLink to="/create">
              {({ isActive }) => (
                <Button
                  variant="ghost"
                  size="sm"
                  className={`rounded-full px-6 transition-all duration-300 ${isActive ? 'bg-zinc-800 text-orange-400 shadow-lg border border-white/5' : 'text-zinc-500 hover:text-zinc-300'}`}
                >
                  Generate
                </Button>
              )}
            </NavLink>
            <NavLink to="/verify">
              {({ isActive }) => (
                <Button
                  variant="ghost"
                  size="sm"
                  className={`rounded-full px-6 transition-all duration-300 ${isActive ? 'bg-zinc-800 text-orange-400 shadow-lg border border-white/5' : 'text-zinc-500 hover:text-zinc-300'}`}
                >
                  Verify
                </Button>
              )}
            </NavLink>
          </nav>

          <div className="text-xs font-mono text-zinc-600">
            V2.0 ALPHA
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 pt-16 relative">
          <Routes>
            <Route path="/" element={<Navigate to="/create" replace />} />
            <Route path="/create" element={<CreationScreen />} />
            <Route path="/verify" element={<DetectionScreen />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}


export default App;
