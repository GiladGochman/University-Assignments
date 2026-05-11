interface PaginationProps {
  activePage: number;
  totalPages: number;
  setActivePage: (page: number) => void;
}

export default function Pagination({
  activePage,
  totalPages,
  setActivePage,
}: PaginationProps) {
  function getPageRange(activePage: number, totalPages: number): number[] {
    if (totalPages <= 5)
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    if (activePage <= 3) return [1, 2, 3, 4, 5];
    if (activePage >= totalPages - 2)
      return Array.from({ length: 5 }, (_, i) => totalPages - 4 + i);
    return [
      activePage - 2,
      activePage - 1,
      activePage,
      activePage + 1,
      activePage + 2,
    ];
  }

  return (
    <div>
      <span>
        page: {activePage} / {totalPages}
      </span>

      <button disabled={activePage === 1} onClick={() => setActivePage(1)}>
        first
      </button>
      <button
        disabled={activePage === 1}
        onClick={() => setActivePage(activePage - 1)}
      >
        previous
      </button>

      {getPageRange(activePage, totalPages).map((page) => (
        <button
          key={page}
          disabled={page === activePage}
          className={page === activePage ? "active" : "not-active"}
          onClick={() => setActivePage(page)}
        >
          {page}
        </button>
      ))}

      <button
        disabled={activePage === totalPages}
        onClick={() => setActivePage(activePage + 1)}
      >
        next
      </button>
      <button
        disabled={activePage === totalPages}
        onClick={() => setActivePage(totalPages)}
      >
        last
      </button>
    </div>
  );
}
