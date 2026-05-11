export function getPageNumbers(currentPage: number, totalPages: number): number[] {
    if (totalPages <= 5) {
        // מחזיר עמודים מ-1 עד totalPages בלבד
        return Array.from({ length: totalPages }, (_, i) => i + 1);
    } else if (currentPage < 3) {
        return [1, 2, 3, 4, 5];
    } else if (currentPage >= 3 && currentPage <= totalPages - 2) {
        return [
            currentPage - 2,
            currentPage - 1,
            currentPage,
            currentPage + 1,
            currentPage + 2,
        ];
    } else {
        return [totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
    }
}
