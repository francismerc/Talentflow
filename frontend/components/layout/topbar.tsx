import { Bell, ChevronDown, Menu, Search } from "lucide-react";

export function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <button
        className="focus-ring mr-3 rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
        onClick={onMenuClick}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </button>
      <div className="relative hidden w-full max-w-md sm:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          aria-label="Global search"
          placeholder="Search candidates, jobs, or skills..."
          className="focus-ring h-9 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-16 text-sm text-primary placeholder:text-slate-400 focus:border-blue-300 focus:bg-white"
        />
        <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400">
          ⌘ K
        </kbd>
      </div>
      <div className="ml-auto flex items-center gap-1.5">
        <button className="focus-ring relative rounded-lg p-2 text-slate-500 hover:bg-slate-100">
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full border-2 border-white bg-danger" />
        </button>
        <div className="mx-2 hidden h-6 w-px bg-slate-200 sm:block" />
        <button className="focus-ring hidden items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 sm:flex">
          Acme Inc.
          <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
        </button>
      </div>
    </header>
  );
}
