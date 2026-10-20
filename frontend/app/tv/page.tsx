"use client";

import { useEffect } from "react";

// The old rotating TV view is replaced by the two fixed line TVs.
// Old links (/tv/, /tv/?slide=2) still land on the current screens.
export default function Page() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tv = params.get("slide") === "2" ? "2" : "1";
    params.delete("slide");
    const query = params.toString();
    window.location.replace(`/tv/${tv}/${query ? `?${query}` : ""}`);
  }, []);
  return null;
}
