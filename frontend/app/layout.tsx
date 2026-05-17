import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MindSpark MVP",
  description: "Children's color comic story generator MVP"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
