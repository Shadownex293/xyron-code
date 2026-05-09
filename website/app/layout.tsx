import type {Metadata} from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { BackgroundElements } from '@/components/background-elements';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export const metadata: Metadata = {
  title: 'Xyron Code',
  description: 'Terminal AI Coding Assistant',
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="id" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-black text-white font-sans antialiased selection:bg-zinc-800 selection:text-white" suppressHydrationWarning>
        <BackgroundElements />
        {children}
      </body>
    </html>
  );
}

