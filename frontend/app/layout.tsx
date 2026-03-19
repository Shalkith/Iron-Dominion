import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'War Game - Multiplayer Strategy',
  description: 'A multiplayer strategy war game',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-100">
        {children}
      </body>
    </html>
  );
}
