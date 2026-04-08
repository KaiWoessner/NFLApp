import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { nflLogoUrl } from "./TeamPicker";

export default function MatchupPicker({ teams, team1, team2, onChange }) {
  const [open, setOpen] = useState(false);
  const [pendingTeams, setPendingTeams] = useState([team1 || "", team2 || ""]);
  const [activeSlot, setActiveSlot] = useState(0);
  const containerRef = useRef(null);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);
  const [popoverStyle, setPopoverStyle] = useState(null);

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
      const popoverChromeHeight = 144;
      const rect = triggerRef.current.getBoundingClientRect();
      const desiredWidth = Math.min(388, window.innerWidth - viewportPadding * 2);
      const left = Math.min(rect.right + 12, window.innerWidth - desiredWidth - viewportPadding);
      const availableHeight = Math.max(320, window.innerHeight - viewportPadding * 2);
      const panelMaxHeight = Math.min(620, availableHeight);
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

  function openPicker() {
    setPendingTeams([team1 || "", team2 || ""]);
    setActiveSlot(team1 ? (team2 ? 0 : 1) : 0);
    setOpen(true);
  }

  function selectTeam(nextTeam, event) {
    event?.stopPropagation();
    setPendingTeams((current) => {
      const next = [...current];
      next[activeSlot] = nextTeam;
      return next;
    });
    if (activeSlot === 0) {
      setActiveSlot(1);
    }
  }

  function applySelection() {
    if (!pendingTeams[0] || !pendingTeams[1]) {
      return;
    }

    onChange(pendingTeams[0], pendingTeams[1]);
    setOpen(false);
  }

  function logoForTeam(teamAbbr) {
    return teams.find((team) => team.abbr === teamAbbr)?.logoUrl || nflLogoUrl();
  }

  return (
    <div ref={containerRef} className="relative shrink-0">
      <button
        ref={triggerRef}
        type="button"
        onClick={openPicker}
        aria-expanded={open}
        className="rounded-xl border border-[#2f382f] bg-[#1f2520] px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#d4d2ca] transition hover:bg-[#262d26] focus:border-[#7f9547]"
      >
        Select
      </button>

      {open && popoverStyle && typeof document !== "undefined"
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
                  Choose two teams
                </p>
                <button
                  type="button"
                  onClick={applySelection}
                  disabled={!pendingTeams[0] || !pendingTeams[1]}
                  className="rounded-full border border-[#2f382f] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#d4d2ca] transition hover:bg-[#262d26] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Done
                </button>
              </div>

              <div className="mb-4 grid grid-cols-2 gap-2">
                {["First Team", "Second Team"].map((label, index) => (
                  <button
                    key={label}
                    type="button"
                    onClick={() => setActiveSlot(index)}
                    className={[
                      "flex items-center gap-2 rounded-2xl border px-3 py-2 text-left transition",
                      activeSlot === index
                        ? "border-[#7f9547] bg-[#293221]"
                        : "border-[#2f382f] bg-[#202621]",
                    ].join(" ")}
                  >
                    <img
                      src={logoForTeam(pendingTeams[index])}
                      alt={pendingTeams[index] || "NFL"}
                      className="h-8 w-8 object-contain"
                    />
                    <span className="min-w-0">
                      <span className="block text-[10px] font-semibold uppercase tracking-[0.18em] text-[#a3a89d]">
                        {label}
                      </span>
                      <span className="block truncate text-sm font-medium text-[#f1eadc]">
                        {pendingTeams[index] || "Select"}
                      </span>
                    </span>
                  </button>
                ))}
              </div>

              <div
                className="thin-scrollbar grid grid-cols-4 gap-2 overflow-y-auto pr-1"
                style={{ maxHeight: `${popoverStyle.maxHeight}px` }}
              >
                {teams.map((team) => (
                  <button
                    key={team.abbr}
                    type="button"
                    onClick={(event) => selectTeam(team.abbr, event)}
                    title={`${team.abbr} - ${team.name}`}
                    aria-label={`Matchup: ${team.abbr} ${team.name}`}
                    className={[
                      "flex aspect-square items-center justify-center rounded-2xl border p-2 transition",
                      pendingTeams.includes(team.abbr)
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
        : null}
    </div>
  );
}
