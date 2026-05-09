"use client"
import { useState, useEffect } from 'react'

export function TerminalMockup() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timer1 = setTimeout(() => setStep(1), 1000)
    const timer2 = setTimeout(() => setStep(2), 2500)
    const timer3 = setTimeout(() => setStep(3), 3500)
    const timer4 = setTimeout(() => setStep(4), 5000)
    
    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
      clearTimeout(timer3)
      clearTimeout(timer4)
    }
  }, [])

  return (
    <div className="w-full max-w-2xl mx-auto rounded-xl overflow-hidden border border-zinc-800 bg-black/80 backdrop-blur-md shadow-2xl relative">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-cyan-500/10 pointer-events-none" />
      <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800/80 bg-zinc-950/50 relative z-10">
        <div className="w-3 h-3 rounded-full bg-zinc-800" />
        <div className="w-3 h-3 rounded-full bg-zinc-800" />
        <div className="w-3 h-3 rounded-full bg-zinc-800" />
        <span className="ml-2 text-[10px] font-mono text-zinc-600 uppercase tracking-widest">xyron-code</span>
      </div>
      <div className="p-6 font-mono text-xs md:text-sm leading-relaxed text-zinc-400 relative z-10 h-[360px] overflow-hidden">
        
        {step >= 0 && (
          <div className="flex gap-3">
            <span className="text-zinc-600">~</span>
            <span className="text-white">git clone https://github.com/Shadownex293/xyron-code.git</span>
          </div>
        )}
        
        {step >= 1 && (
          <>
            <div className="text-zinc-600 ml-5 py-1">Cloning into 'xyron-code'...</div>
            <div className="flex gap-3 ml-5">
              <span className="text-zinc-500">done.</span>
            </div>
            <div className="h-4" />
            <div className="flex gap-3">
              <span className="text-zinc-600">~</span>
              <span className="text-white">cd xyron-code &amp;&amp; bash install.sh</span>
            </div>
          </>
        )}

{step >= 2 && (
  <>
    <div className="h-4" />
    <div className="text-indigo-400">  ██╗  ██╗██╗   ██╗██████╗  ██████╗ ███╗  ██╗</div>
    <div className="text-indigo-400">  ╚██╗██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗ ██║</div>
    <div className="text-indigo-400">   ╚███╔╝  ╚████╔╝ ██████╔╝██║   ██║██╔██╗██║</div>
    <div className="text-indigo-400">   ██╔██╗   ╚██╔╝  ██╔══██╗██║   ██║██║╚████║</div>
    <div className="text-indigo-400">  ██╔╝╚██╗   ██║   ██║  ██║╚██████╔╝██║ ╚███║</div>
    <div className="text-indigo-400">  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝</div>
    <div className="h-6" />
  </>
)}

        {step >= 3 && (
          <>
            <div className="flex gap-3">
              <span className="text-white">Python: /usr/bin/python3</span>
            </div>
            <div className="flex gap-3">
              <span className="text-emerald-400">Semua dependencies terpasang.</span>
            </div>
            <div className="h-6" />
          </>
        )}

        {step >= 4 && (
          <div className="flex gap-3 items-center mt-1">
            <span className="text-zinc-600">~</span>
            <span className="text-white">xyroncode</span>
            <span className="w-2 h-4 bg-white block animate-pulse" />
          </div>
        )}
      </div>
    </div>
  )
}
