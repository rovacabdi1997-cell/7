import { DataProvider } from "@/features/data/DataProvider";
import { LineTv } from "@/features/screens/LineTv";

export const metadata = { title: "TV 2 · Gury garyndy" };

export default function Page() {
  return (
    <DataProvider line="gury-garyndy">
      <LineTv tvId="tv-2" />
    </DataProvider>
  );
}
