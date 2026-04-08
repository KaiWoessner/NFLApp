import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export function nflLogoUrl() {
  return "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png";
}

export default function TeamPicker({ title, teams, value, onChange, variant = "card" }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);
  const [popoverStyle, setPopoverStyle] = useState(null);
  const selectedTeam = teams.find((team) => team.abbr === value) || null;
  const headerColor = "#e6dfd2";
  const displayValue = selectedTeam ? selectedTeam.name : "Team";
  const currentLogoUrl = selectedTeam?.logoUrl || nflLogoUrl();
  const pickerOptions = [{ abbr: "", name: "NFL", logoUrl: nflLogoUrl() }, ...teams];

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handlePointerDown(event) {
      const clickedInsideTrigger = containerRef.current?.contains(event.target);
      const clickedInsidePopover = popoverRef.current?.contains(event.target);
      if (!clickedInsideTrigger && !clickedInsidePopover) {
        setOpen(false);
      }
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    function updatePopoverPosition() {
      if (!triggerRef.current) {
        return;
      }

      const viewportPadding = 12;
      const popoverChromeHeight = 92;
      const rect = triggerRef.current.getBoundingClientRect();
      const desiredWidth = Math.min(388, window.innerWidth - viewportPadding * 2);
      const left = Math.min(rect.right + 12, window.innerWidth - desiredWidth - viewportPadding);
      const availableHeight = Math.max(280, window.innerHeight - viewportPadding * 2);
      const panelMaxHeight = Math.min(560, availableHeight);
      const top = Math.min(
        Math.max(viewportPadding, rect.top),
        window.innerHeight - panelMaxHeight - viewportPadding,
      );

      setPopoverStyle({
        top: Math.max(viewportPadding, top),
        left: Math.max(viewportPadding, left),
        width: desiredWidth,
        panelMaxHeight,
        maxHeight: Math.max(180, panelMaxHeight - popoverChromeHeight),
      });
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    window.addEventListener("resize", updatePopoverPosition);
    window.addEventListener("scroll", updatePopoverPosition, true);
    updatePopoverPosition();
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("resize", updatePopoverPosition);
      window.removeEventListener("scroll", updatePopoverPosition, true);
    };
  }, [open]);

  function selectTeam(nextValue, event) {
    event?.stopPropagation();
    onChange(nextValue);
    setOpen(false);
  }

  const pickerPopover = open && popoverStyle && typeof document !== "undefined"
    ? createPortal(
        <div
          ref={popoverRef}
          className="fixed z-[100] rounded-[1.75rem] border border-[#2f382f] bg-[#1f2520] p-4 shadow-2xl"
          onClick={(event) => event.stopPropagation()}
          onMouseDown={(event) => event.stopPropagation()}
          style={{
            top: `${popoverStyle.top}px`,
            left: `${popoverStyle.left}px`,
            width: `${popoverStyle.width}px`,
            maxHeight: `${popoverStyle.panelMaxHeight}px`,
          }}
        >
          <div className="mb-3 flex items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.2em] text-[#a3a89d]">
              Choose a team
            </p>
            {variant === "card" ? (
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-full border border-[#2f382f] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#d4d2ca] transition hover:bg-[#262d26]"
              >
                Done
              </button>
            ) : null}
          </div>

          <div
            className="thin-scrollbar grid grid-cols-4 gap-2 overflow-y-auto pr-1"
            style={{ maxHeight: `${popoverStyle.maxHeight}px` }}
          >
            {pickerOptions.map((team) => (
              <button
                key={team.abbr}
                type="button"
                onClick={(event) => selectTeam(team.abbr, event)}
                title={team.abbr ? `${team.abbr} - ${team.name}` : team.name}
                aria-label={team.abbr ? `${title}: ${team.abbr} ${team.name}` : `${title}: ${team.name}`}
                className={[
                  "flex aspect-square items-center justify-center rounded-2xl border p-2 transition",
                  value === team.abbr
                    ? "border-[#7f9547] bg-[#293221] shadow-[0_0_0_1px_rgba(127,149,71,0.18)]"
                    : "border-[#2f382f] bg-[#1f2520] hover:border-[#4c5a49] hover:bg-[#262d26]",
                ].join(" ")}
              >
                <img
                  src={team.logoUrl || nflLogoUrl()}
                  alt={team.name}
                  className="h-10 w-10 object-contain"
                />
              </button>
            ))}
          </div>
        </div>,
        document.body,
      )
    : null;

  if (variant === "button") {
    return (
      <div ref={containerRef} className="relative shrink-0">
        <button
          ref={triggerRef}
          type="button"
          onClick={() => setOpen((current) => !current)}
          aria-expanded={open}
          className="rounded-xl border border-[#2f382f] bg-[#1f2520] px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#d4d2ca] transition hover:bg-[#262d26] focus:border-[#7f9547]"
        >
          Select
        </button>
        {pickerPopover}
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative rounded-3xl border border-[#2b342d] bg-[#202621]/92 p-4 shadow-sm">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-[#2f382f] bg-[#1f2520] shadow-sm">
            <img
              src={currentLogoUrl}
              alt={selectedTeam ? selectedTeam.name : "NFL"}
              className="h-10 w-10 object-contain"
            />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs uppercase tracking-[0.22em] text-[#a3a89d]">{title}</p>
            <p
              className="text-sm font-semibold leading-5"
              style={{ color: headerColor }}
            >
              {displayValue}
            </p>
          </div>
        </div>

        <button
          ref={triggerRef}
          type="button"
          onClick={() => setOpen((current) => !current)}
          aria-expanded={open}
          className="shrink-0 rounded-2xl border border-[#2f382f] bg-[#1f2520] px-4 py-3 text-left text-sm text-[#f4ede2] outline-none transition hover:bg-[#262d26] focus:border-[#7f9547]"
        >
          <span className="block whitespace-nowrap text-xs font-semibold uppercase tracking-[0.18em] text-[#d4d2ca]">
            {open ? "Close" : "Select"}
          </span>
        </button>
      </div>

      {pickerPopover}
    </div>
  );
}
