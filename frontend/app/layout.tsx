import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "@/styles/globals.css";
import "@/styles/presentation-theme.css";
import { PresentationTheme } from "@/components/PresentationTheme";

export const metadata: Metadata = {
  icons: { icon: "/tv/support/logo.png" },
  title: "Önümçilik gözegçiligi",
  description: "Gipsokarton we gury garyndy önümçiliginiň gözegçilik paneli",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="tk">
      <body><PresentationTheme />{children}</body>
    </html>
  );
}
