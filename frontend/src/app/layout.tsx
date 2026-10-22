import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MTIS — Malaysian Thesis Institution System",
  description: "AI-Powered Research Guide & Thesis Structuring for Malaysian Higher Education",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
