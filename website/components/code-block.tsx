import { CopyButton } from './copy-button'
import { ReactNode } from 'react'

export function CodeBlock({ lang, code, children }: { lang: string, code: string, children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-zinc-900 bg-zinc-950 overflow-hidden w-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-900 bg-zinc-950">
        <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">{lang}</span>
        <CopyButton text={code} />
      </div>
      <div className="p-4 font-mono text-sm overflow-x-auto text-zinc-300 leading-relaxed">
        {children || <pre><code>{code}</code></pre>}
      </div>
    </div>
  )
}
