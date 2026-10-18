import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { DataProvider } from "@/features/data/DataProvider";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Önümçilik gözegçiligi",
  description: "Gipsokarton we gury garyndy önümçiliginiň gözegçilik paneli",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="tk">
      <body>
        <DataProvider>{children}</DataProvider>
      </body>
    </html>
  );
}
