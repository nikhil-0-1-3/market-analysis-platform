import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "marketsense — your daily market briefing",
  description: "Humanized AI market dashboard with live signals.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
