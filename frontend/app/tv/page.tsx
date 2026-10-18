import { Suspense } from "react";
import { TvView } from "@/features/screens/TvView";

export const metadata = { title: "TV görnüşi" };

export default function Page() {
  return (
    <Suspense>
      <TvView />
    </Suspense>
  );
}
