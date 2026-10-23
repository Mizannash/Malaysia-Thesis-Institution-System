import "./globals.css";
import type { Metadata } from "next";
import { LanguageProvider } from "@/lib/LanguageContext";

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
      <body>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
