import { useEffect, useState } from "react";
import ActivityTerrain from "./ActivityTerrain";

const USERNAME = "DoesntMatterICare";
const API_URL = "https://github-contributions-api.jogruber.de/v4/" + USERNAME + "?y=last";

type Contribution = { date: string; count: number; level: number };
type ApiResponse = { total?: Record<string, number>; contributions?: Contribution[] };
type ActivityData = { data: number[]; endDate: string; total: number };

function isoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function todayUTC() {
  const now = new Date();
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
}

export default function App() {
  const [activity, setActivity] = useState<ActivityData | null>(null);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setActivity(null);
    setError("");

    fetch(API_URL, { signal: controller.signal, headers: { Accept: "application/json" } })
      .then((response) => {
        if (!response.ok) throw new Error("The contribution service returned " + response.status + ".");
        return response.json() as Promise<ApiResponse>;
      })
      .then((payload) => {
        if (!Array.isArray(payload.contributions)) {
          throw new Error("The contribution service returned an unexpected response.");
        }
        const end = todayUTC();
        const start = new Date(end.getTime() - 181 * 86400000);
        const byDate = new Map(payload.contributions.map((entry) => [entry.date, entry.count]));
        const data = Array.from({ length: 182 }, (_, index) => {
          const date = new Date(start.getTime() + index * 86400000);
          return byDate.get(isoDate(date)) ?? 0;
        });
        setActivity({
          data,
          endDate: isoDate(end),
          total: data.reduce((sum, count) => sum + count, 0)
        });
      })
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setError(cause instanceof Error ? cause.message : "Unable to load GitHub contribution data.");
      });

    return () => controller.abort();
  }, [reload]);

  return (
    <main className="min-h-screen bg-zinc-950 px-4 py-6 text-zinc-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <nav className="flex items-center justify-between gap-4 border-b border-zinc-800 pb-5">
          <a className="flex items-center gap-3 text-xs font-semibold tracking-[0.16em] text-zinc-200 no-underline" href="https://github.com/DoesntMatterICare">
            <span className="grid size-8 place-items-center rounded-lg border border-emerald-500/50 font-serif text-lg text-emerald-300">R</span>
            DOESNTMATTERICARE
          </a>
          <span className="flex items-center gap-2 text-[10px] tracking-[0.13em] text-zinc-500"><span className="size-1.5 rounded-full bg-emerald-400" /> PUBLIC GITHUB DATA</span>
        </nav>

        <header className="max-w-3xl py-14 sm:py-20">
          <p className="mb-4 text-[10px] tracking-[0.2em] text-emerald-300">A DIFFERENT VIEW OF THE GREEN SQUARES</p>
          <h1 className="text-6xl font-semibold leading-[0.9] tracking-[-0.075em] sm:text-8xl">Activity<br /><span className="font-serif font-normal italic text-emerald-300">Terrain.</span></h1>
          <p className="mt-7 max-w-xl text-sm leading-7 text-zinc-400 sm:text-base">Six months of GitHub activity, lifted into a little landscape. Drag it around, inspect an individual day, or flatten it back into a heatmap.</p>
          <div className="mt-7 flex flex-wrap items-center gap-x-4 gap-y-2 text-[10px] tracking-[0.14em] text-zinc-500"><span><b className="text-zinc-200">182</b> DAYS</span><span className="h-3 w-px bg-zinc-700" /><span><b className="text-zinc-200">01</b> PROFILE</span><span className="h-3 w-px bg-zinc-700" /><span>INTERACTIVE CANVAS</span></div>
        </header>

        {activity ? (
          <>
            <ActivityTerrain data={activity.data} endDate={activity.endDate} title="DoesntMatterICare · Contributions" />
            <div className="mt-4 flex items-start gap-3 text-xs leading-6 text-zinc-500"><span className="mt-2 size-1.5 shrink-0 rounded-full bg-emerald-400" /><p className="m-0"><strong className="font-medium text-emerald-200">{activity.total.toLocaleString("en-US")}</strong> public contributions in this window. The source API caches results for up to one hour. Private activity is not included unless GitHub exposes it on the public contribution graph.</p></div>
          </>
        ) : error ? (
          <section className="grid min-h-72 justify-items-center content-center gap-4 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-8 text-center">
            <span className="grid size-8 place-items-center rounded-full border border-amber-700 text-amber-300">!</span>
            <h2 className="m-0 text-lg font-medium">Contribution data unavailable</h2>
            <p className="max-w-xl break-words text-sm leading-6 text-zinc-400">{error}</p>
            <button className="rounded-full border border-emerald-700 bg-emerald-950 px-4 py-2 text-sm text-emerald-100 hover:bg-emerald-900" onClick={() => setReload((value) => value + 1)}>Try again</button>
          </section>
        ) : (
          <section className="grid min-h-72 justify-items-center content-center gap-4 rounded-3xl border border-zinc-800 bg-zinc-900/70 text-sm text-zinc-400"><span className="size-5 animate-spin rounded-full border border-zinc-700 border-t-emerald-300" />Reading the contribution graph…</section>
        )}

        <footer className="mt-10 flex flex-col gap-4 border-t border-zinc-800 pt-5 text-[10px] tracking-[0.12em] text-zinc-500 sm:flex-row sm:items-center sm:justify-between">
          <p className="m-0">BUILT TO BE EXPLORED, NOT JUST LOOKED AT.</p>
          <div className="flex flex-wrap items-center gap-3"><a className="text-zinc-400 hover:text-emerald-300" href="https://github.com/DoesntMatterICare">GITHUB PROFILE ↗</a><span>·</span><a className="text-zinc-400 hover:text-emerald-300" href="https://github.com/grubersjoe/github-contributions-api">DATA SOURCE ↗</a><span>·</span><a className="text-zinc-400 hover:text-emerald-300" href="https://kokonutui.com">ORIGINAL COMPONENT ↗</a></div>
        </footer>
      </div>
    </main>
  );
}
