export default function PaginationBar({ pagination, onPageChange }) {
  if (!pagination?.isPaginated || pagination.totalGames === 0) {
    return null;
  }

  return (
    <div className="surface-card mb-6 grid grid-cols-[96px_minmax(0,1fr)_96px] items-center gap-3 rounded-[2rem] px-4 py-4 sm:grid-cols-[112px_minmax(0,1fr)_112px] sm:px-5">
      <button
        type="button"
        disabled={pagination.page === 1}
        onClick={() => onPageChange(pagination.page - 1)}
        className="rounded-2xl border border-slate-900/10 px-3 py-2.5 text-sm font-semibold text-slate-800 transition hover:bg-slate-900 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
      >
        Previous
      </button>

      <p className="px-2 text-center text-sm leading-5 text-slate-600">
        <span className="block sm:inline">
          Showing games {pagination.startIndex}-{pagination.endIndex} of {pagination.totalGames}
        </span>
        <span className="hidden sm:inline"> • </span>
        <span className="block sm:inline">
          Page {pagination.page} of {pagination.totalPages}
        </span>
      </p>

      <button
        type="button"
        disabled={pagination.page === pagination.totalPages}
        onClick={() => onPageChange(pagination.page + 1)}
        className="rounded-2xl border border-slate-900/10 px-3 py-2.5 text-sm font-semibold text-slate-800 transition hover:bg-slate-900 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
      >
        Next
      </button>
    </div>
  );
}
