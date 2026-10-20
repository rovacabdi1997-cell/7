"use client";
import { useEffect } from "react";

export function PresentationTheme() {
  useEffect(() => {
    const apply = () => {
      document.documentElement.dataset.tema = new URLSearchParams(location.search).get("tema") === "koyu" ? "koyu" : "acik";
    };
    apply();
    window.addEventListener("popstate", apply);
    return () => window.removeEventListener("popstate", apply);
  }, []);
  return null;
}
