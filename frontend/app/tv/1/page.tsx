import { DataProvider } from "@/features/data/DataProvider";
import { LineTv } from "@/features/screens/LineTv";

export const metadata = { title: "TV 1 · Gipsokarton" };

export default function Page() {
  return (
    <DataProvider line="gipsokarton">
      <LineTv tvId="tv-1" />
    </DataProvider>
  );
}
