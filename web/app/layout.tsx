import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PII Redaction & Contextual Logo Pseudonymization System",
  description: "Enterprise PII Detection, Contextual Image Logo Pseudonymization, and Evaluation Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-[#080c14] text-slate-100">
        {children}
      </body>
    </html>
  );
}
