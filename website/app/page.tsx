import { Terminal, Zap, Target, Database, RefreshCcw, Map as MapIcon, Wrench, Github } from "lucide-react"
import Link from "next/link"
import { TerminalMockup } from "@/components/terminal-mockup"
import { CodeBlock } from "@/components/code-block"
import { ScrollReveal } from "@/components/scroll-reveal"

export default function Page() {
  return (
    <div className="min-h-screen bg-transparent text-white">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-900 bg-black/50 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-indigo-400" />
            <span className="font-bold text-sm tracking-tight text-white">XyronCodeX</span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <a href="#tentang" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Tentang</a>
            <a href="#fitur" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Fitur</a>
            <a href="#install" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Install</a>
            <a href="#commands" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Commands</a>
            <a href="https://github.com/Shadownex293/xyron-code" target="_blank" rel="noreferrer" className="flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-24">
        <section className="max-w-5xl mx-auto px-6 flex flex-col items-center text-center mb-32">
          <ScrollReveal delay={0.1}>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-[10px] uppercase tracking-widest text-indigo-300 mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
              Terminal AI Coding Assistant
            </div>
          </ScrollReveal>
          
          <ScrollReveal delay={0.2}>
            <h1 className="text-5xl md:text-7xl font-semibold tracking-tighter text-white mb-6">
              Ngoding lebih cepat.
              <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">Di dalam terminal.</span>
            </h1>
          </ScrollReveal>

          <ScrollReveal delay={0.3}>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Xyron Code beroperasi secara langsung di terminal, dilengkapi file viewer dan command executor tanpa bergantung pada browser.
            </p>
          </ScrollReveal>
          
          <ScrollReveal delay={0.4}>
            <div className="flex items-center justify-center gap-4 flex-col sm:flex-row">
              <a href="#install" className="h-12 px-8 flex items-center justify-center rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white font-medium text-sm transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)]">
                Mulai Install
              </a>
              <a href="https://github.com/Shadownex293/xyron-code" target="_blank" rel="noreferrer" className="h-12 px-8 flex items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900/50 text-white font-medium text-sm hover:bg-zinc-800 transition-colors">
                Lihat Repository
              </a>
            </div>
          </ScrollReveal>
        </section>

        <section className="max-w-5xl mx-auto px-6 mb-32">
          <ScrollReveal delay={0.5}>
            <TerminalMockup />
          </ScrollReveal>
        </section>

        <section id="tentang" className="max-w-5xl mx-auto px-6 mb-32">
          <ScrollReveal>
            <div className="mb-12">
              <h2 className="text-3xl font-semibold tracking-tight text-white mb-4">Murni CLI. Murni Python.</h2>
              <p className="text-zinc-400 max-w-xl leading-relaxed">
                Dibuat khusus untuk terminal environment termasuk setup yang terbatas seperti Termux di Android. Punya banyak provider AI bawaan yang bisa disesuaikan kebutuhan.
              </p>
            </div>
          </ScrollReveal>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[ 
              { num: '13', label: 'AI Provider' },
              { num: '7', label: 'Built-in Tools' },
              { num: '4', label: 'Skill Modes' },
              { num: '3', label: 'Dependencies' }
            ].map((stat, i) => (
              <ScrollReveal key={i} delay={0.1 * i}>
                <div className="group border border-zinc-900 hover:border-indigo-500/50 bg-zinc-950/50 hover:bg-indigo-500/5 p-6 rounded-xl flex flex-col justify-between h-32 transition-all duration-300 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-transparent to-indigo-500/0 group-hover:from-indigo-500/10 transition-all duration-500" />
                  <span className="text-4xl font-bold text-white tracking-tighter relative z-10">{stat.num}</span>
                  <span className="text-xs uppercase tracking-widest text-zinc-500 group-hover:text-indigo-400 transition-colors relative z-10">{stat.label}</span>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </section>

        <section id="fitur" className="max-w-5xl mx-auto px-6 mb-32">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[ 
              { icon: Zap, title: 'Streaming Real-time', desc: 'Response dikelola secepatnya. Mampu auto-continue saat response awal secara tak terduga terpotong.' },
              { icon: Wrench, title: 'Built-in Tools', desc: 'Eksekusi shell command dan ubah isi file secara mandiri tanpa keluar dari antarmuka utama program.' },
              { icon: Target, title: 'Skill Detection', desc: 'Otomatisasi pengenalan dan penerapan alur kerja berbasiskan apa yang sedang menjadi target eksekusi utama.' },
              { icon: Database, title: 'Session Memory', desc: 'Data obrolan disimpan otomatis ke sistem agar dapat dilanjutkan kapanpun bahkan setelah terputus di tengah jalan.' },
              { icon: RefreshCcw, title: 'Multi-Provider', desc: 'Transisi yang simpel antarmodel dari berbagai arsitektur penyedia komputasi global tanpa batasan rumit.' },
              { icon: MapIcon, title: 'Task Roadmap', desc: 'Pedoman terstruktur otomatis tercipta untuk proyek berskala kompleks guna menjaga stabilitas fokus pengerjaan.' }
            ].map((Feature, i) => (
              <ScrollReveal key={i} delay={0.1 * i}>
                <div className="p-6 rounded-xl border border-zinc-900 bg-zinc-950/50 hover:border-zinc-700 transition-colors h-full">
                  <Feature.icon className="w-6 h-6 text-indigo-400 mb-6" />
                  <h3 className="text-lg font-medium text-white mb-2">{Feature.title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{Feature.desc}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </section>

        <section className="max-w-5xl mx-auto px-6 mb-32">
           <ScrollReveal>
             <h2 className="text-lg font-semibold tracking-tight uppercase text-indigo-400 text-xs mb-6">Integrasi API Tersedia</h2>
             <div className="flex flex-wrap gap-2">
               {["Gemini", "Groq", "Cerebras", "Mistral", "SambaNova", "DeepSeek", "OpenRouter", "xAI Grok", "Together AI", "NVIDIA NIM", "Kimi", "Qwen", "MiniMax"].map(provider => (
                  <div key={provider} className="px-4 py-2 rounded-lg border border-zinc-800 bg-zinc-950/50 hover:bg-zinc-800 text-sm font-medium text-zinc-300 transition-colors cursor-default">
                    {provider}
                  </div>
               ))}
             </div>
           </ScrollReveal>
        </section>

        <section id="install" className="max-w-5xl mx-auto px-6 mb-32">
          <ScrollReveal>
            <h2 className="text-3xl font-semibold tracking-tight text-white mb-12">Pemasangan</h2>
          </ScrollReveal>
          
          <div className="space-y-12">
            {[ 
              { step: 1, title: 'Salin Repository', desc: 'Ambil code dari source utama di GitHub ke dalam penyimpanan perangkat yang sedang digunakan.', code: 'git clone https://github.com/Shadownex293/xyron-code.git\ncd xyron-code' },
              { step: 2, title: 'Jalankan Skrip', desc: 'Skrip ini akan mengelola pemasangan dependensi yang diperlukan agar sistem dapat berjalan.', code: 'bash install.sh\nexport PATH="$HOME/.local/bin:$PATH"' },
              { step: 3, title: 'Selesaikan Setelan', desc: 'Tentukan pilihan koneksi parameter dan selesaikan integrasi kredensial lokal ke dalam program.', code: 'xyroncodex' }
            ].map((item, i) => (
              <ScrollReveal key={i} delay={0.1}>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                  <div>
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-sm">{item.step}</div>
                      <h3 className="text-xl font-medium text-white">{item.title}</h3>
                    </div>
                    <p className="text-zinc-400 pl-12 text-sm leading-relaxed">{item.desc}</p>
                  </div>
                  <CodeBlock lang="bash" code={item.code} />
                </div>
              </ScrollReveal>
            ))}
          </div>
        </section>

        <section id="commands" className="max-w-5xl mx-auto px-6">
          <ScrollReveal>
            <h2 className="text-3xl font-semibold tracking-tight text-white mb-10">Daftar Commands</h2>
            <div className="overflow-x-auto rounded-xl border border-zinc-900 bg-zinc-950/50">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-zinc-900 bg-black/50">
                    <th className="py-4 px-6 text-xs font-mono uppercase tracking-widest text-zinc-500 font-medium">Command</th>
                    <th className="py-4 px-6 text-xs font-mono uppercase tracking-widest text-zinc-500 font-medium">Fungsi</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {[ 
                    { cmd: '/help', desc: 'Tampilkan semua menu command bantuan.' },
                    { cmd: '/provider', desc: 'Ganti spesifikasi pemrosesan utama via wizard.' },
                    { cmd: '/model [id]', desc: 'Langsung pindah ke target ID spesifikasi.' },
                    { cmd: '/roadmap', desc: 'Tampilkan alur pengerjaan yang sedang dipantau.' },
                    { cmd: '/clear', desc: 'Pusatkan obrolan ke tahap awal secara internal.' },
                    { cmd: '/tokens', desc: 'Lacak alokasi kapasitas pemrosesan interaksi saat ini.' }
                  ].map((row, i) => (
                    <tr key={i} className="border-b border-zinc-900/50 hover:bg-zinc-900/30 transition-colors">
                      <td className="py-4 px-6 font-mono text-indigo-300 whitespace-nowrap">{row.cmd}</td>
                      <td className="py-4 px-6 text-zinc-400">{row.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ScrollReveal>
        </section>
      </main>

      <footer className="border-t border-zinc-900 bg-black/50">
        <div className="max-w-5xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-zinc-500 font-medium">
            XyronCode &bull; oleh ShadowNex
          </div>
          <div className="flex gap-6">
            <a href="https://github.com/Shadownex293/xyron-code" target="_blank" rel="noreferrer" className="text-sm font-medium text-zinc-500 hover:text-white transition-colors">GitHub</a>
            <a href="https://t.me/SHADOWNEX2" target="_blank" rel="noreferrer" className="text-sm font-medium text-zinc-500 hover:text-white transition-colors">Telegram</a>
            <a href="https://tiktok.com/@mr.shadownex" target="_blank" rel="noreferrer" className="text-sm font-medium text-zinc-500 hover:text-white transition-colors">TikTok</a>
            <a href="https://saweria.co/shadownex" target="_blank" rel="noreferrer" className="text-sm font-medium text-zinc-500 hover:text-white transition-colors">Saweria</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

