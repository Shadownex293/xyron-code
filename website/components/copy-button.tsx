"use client"
import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

export function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button onClick={handleCopy} className="text-zinc-500 hover:text-zinc-300 transition-colors outline-none">
      {copied ? <Check className="w-4 h-4 text-white" /> : <Copy className="w-4 h-4" />}
    </button>
  )
}
