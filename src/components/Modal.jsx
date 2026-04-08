import { useEffect } from "react";

export default function Modal({ open, title, onClose, children }) {
  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handleKeydown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/60 px-4 py-8 backdrop-blur-sm">
      <div className="w-full max-w-7xl overflow-x-hidden rounded-[2rem] bg-[#f8f6ee] p-4 shadow-2xl md:p-6">
        <div className="mb-5 flex items-start justify-between gap-4 border-b border-slate-900/10 pb-4">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Selected Game</p>
            <h2 className="mt-2 font-display text-3xl leading-tight text-slate-950">{title}</h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-2xl border border-slate-900/10 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-950 hover:text-white"
          >
            Close
          </button>
        </div>

        {children}
      </div>
    </div>
  );
}
