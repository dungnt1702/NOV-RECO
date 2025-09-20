/**
 * Pagination Component
 * Reusable pagination component with search and filtering support
 */

class PaginationComponent {
  constructor(options = {}) {
    this.currentPage = 1;
    this.pageSize = 20;
    this.totalItems = 0;
    this.totalPages = 0;
    this.items = [];
    this.filteredItems = [];
    this.searchQuery = '';
    
    // Configuration
    this.config = {
      showPageSizeSelector: true,
      showPageInfo: true,
      maxVisiblePages: 5,
      onPageChange: null,
      onPageSizeChange: null,
      onSearch: null,
      ...options
    };
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.render();
  }
  
  setupEventListeners() {
    // Page size change
    const pageSizeSelect = document.getElementById('page-size-select');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', (e) => {
        this.changePageSize(parseInt(e.target.value));
      });
    }
  }
  
  setData(items) {
    this.items = items || [];
    this.filteredItems = [...this.items];
    this.totalItems = this.filteredItems.length;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    this.currentPage = Math.min(this.currentPage, Math.max(1, this.totalPages));
    this.render();
  }
  
  setSearchQuery(query) {
    this.searchQuery = query.toLowerCase();
    this.applyFilters();
  }
  
  applyFilters() {
    if (!this.searchQuery) {
      this.filteredItems = [...this.items];
    } else {
      this.filteredItems = this.items.filter(item => {
        // Default search implementation - can be overridden
        return Object.values(item).some(value => 
          String(value).toLowerCase().includes(this.searchQuery)
        );
      });
    }
    
    this.totalItems = this.filteredItems.length;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    this.currentPage = Math.min(this.currentPage, Math.max(1, this.totalPages));
    
    // Call search callback if provided
    if (this.config.onSearch) {
      this.config.onSearch(this.filteredItems);
    }
    
    this.render();
  }
  
  getCurrentPageItems() {
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return this.filteredItems.slice(startIndex, endIndex);
  }
  
  changePage(page) {
    if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
      this.currentPage = page;
      this.render();
      
      // Call page change callback if provided
      if (this.config.onPageChange) {
        this.config.onPageChange(this.getCurrentPageItems(), this.currentPage);
      }
    }
  }
  
  prevPage() {
    this.changePage(this.currentPage - 1);
  }
  
  nextPage() {
    this.changePage(this.currentPage + 1);
  }
  
  changePageSize(newPageSize) {
    this.pageSize = newPageSize;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    this.currentPage = Math.min(this.currentPage, Math.max(1, this.totalPages));
    this.render();
    
    // Call page size change callback if provided
    if (this.config.onPageSizeChange) {
      this.config.onPageSizeChange(this.getCurrentPageItems(), this.pageSize);
    }
  }
  
  render() {
    this.renderPaginationInfo();
    this.renderPageNavigation();
    this.renderPageSizeSelector();
  }
  
  renderPaginationInfo() {
    const infoElement = document.getElementById('pagination-info-text');
    if (!infoElement || !this.config.showPageInfo) return;
    
    if (this.totalItems === 0) {
      infoElement.textContent = 'Không có dữ liệu';
      return;
    }
    
    const startIndex = (this.currentPage - 1) * this.pageSize + 1;
    const endIndex = Math.min(this.currentPage * this.pageSize, this.totalItems);
    
    infoElement.textContent = `Hiển thị ${startIndex}-${endIndex} trong tổng số ${this.totalItems} mục`;
  }
  
  renderPageNavigation() {
    const prevButton = document.getElementById('page-prev');
    const nextButton = document.getElementById('page-next');
    const pageNumbers = document.getElementById('page-numbers');
    
    if (!prevButton || !nextButton || !pageNumbers) return;
    
    // Update prev/next buttons
    prevButton.disabled = this.currentPage <= 1;
    nextButton.disabled = this.currentPage >= this.totalPages;
    
    // Clear page numbers
    pageNumbers.innerHTML = '';
    
    if (this.totalPages <= 1) return;
    
    // Calculate visible page range
    const maxVisible = this.config.maxVisiblePages;
    let startPage = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(this.totalPages, startPage + maxVisible - 1);
    
    // Adjust if we're near the end
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // Add page numbers
    for (let i = startPage; i <= endPage; i++) {
      const pageButton = document.createElement('button');
      pageButton.className = `page-link ${i === this.currentPage ? 'active' : ''}`;
      pageButton.textContent = i;
      pageButton.onclick = () => this.changePage(i);
      pageNumbers.appendChild(pageButton);
    }
  }
  
  renderPageSizeSelector() {
    const pageSizeSelect = document.getElementById('page-size-select');
    if (!pageSizeSelect || !this.config.showPageSizeSelector) return;
    
    pageSizeSelect.value = this.pageSize;
  }
  
  // Public methods for external control
  reset() {
    this.currentPage = 1;
    this.pageSize = 20;
    this.searchQuery = '';
    this.filteredItems = [...this.items];
    this.totalItems = this.filteredItems.length;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    this.render();
  }
  
  refresh() {
    this.applyFilters();
  }
}

// Global pagination component instance
window.paginationComponent = new PaginationComponent({
  onPageChange: (items, page) => {
    console.log(`Page changed to ${page}, showing ${items.length} items`);
  },
  onPageSizeChange: (items, pageSize) => {
    console.log(`Page size changed to ${pageSize}, showing ${items.length} items`);
  },
  onSearch: (filteredItems) => {
    console.log(`Search applied, ${filteredItems.length} items found`);
  }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PaginationComponent;
}
