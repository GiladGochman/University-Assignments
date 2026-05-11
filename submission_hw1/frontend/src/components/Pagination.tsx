import { useNotes } from '../contexts/NotesContext';

export default function Pagination() {
  const { state, dispatch } = useNotes();
  const { currentPage, total } = state;
  const totalPages = Math.ceil(total / 10);

  const handlePageChange = (page: number) => {
    dispatch({ type: 'SET_PAGE', payload: page });
  };

  const getPageRange = (activePage: number, total: number): number[] => {
    if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
    if (activePage <= 3) return [1, 2, 3, 4, 5];
    if (activePage >= total - 2)
      return Array.from({ length: 5 }, (_, i) => total - 4 + i);
    return [activePage - 2, activePage - 1, activePage, activePage + 1, activePage + 2];
  };

  const pageRange = getPageRange(currentPage, totalPages);

  return (
    <>
      <span data-testid="page-info">
        page: {currentPage} / {totalPages}
      </span>
      <div>
        <button
          data-testid="first"
          name="first"
          onClick={() => handlePageChange(1)}
          disabled={currentPage === 1}
        >
          first
        </button>
        <button
          data-testid="previous"
          name="previous"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          previous
        </button>

        {pageRange.map((page) => (
          <button
            key={page}
            data-testid={`page-${page}`}
            name={`page-${page}`}
            className={page === currentPage ? 'active' : 'not-active'}
            onClick={() => handlePageChange(page)}
            disabled={page === currentPage}
          >
            {page}
          </button>
        ))}

        <button
          data-testid="next"
          name="next"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          next
        </button>
        <button
          data-testid="last"
          name="last"
          onClick={() => handlePageChange(totalPages)}
          disabled={currentPage === totalPages}
        >
          last
        </button>
      </div>
    </>
  );
}
