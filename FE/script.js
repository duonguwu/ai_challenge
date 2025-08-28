// Configuration
const API_BASE_URL = 'http://localhost:8000';
const GRID_SIZE = 20; // 5x4 grid
const ITEMS_PER_PAGE = GRID_SIZE;

// Global state
let currentResults = [];
let currentPage = 0;
let currentQueries = [];
let currentObjects = [];

// DOM elements
const queryInput = document.getElementById('queryInput');
const objectInput = document.getElementById('objectInput');
const searchBtn = document.getElementById('searchBtn');
const searchMoreBtn = document.getElementById('searchMoreBtn');
const resultsSection = document.getElementById('resultsSection');
const gridContainer = document.getElementById('gridContainer');
const paginationInfo = document.getElementById('paginationInfo');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// Event listeners
searchBtn.addEventListener('click', handleSearch);
searchMoreBtn.addEventListener('click', handleSearchMore);
prevBtn.addEventListener('click', () => changePage(-1));
nextBtn.addEventListener('click', () => changePage(1));

// Handle search button click
async function handleSearch() {
    const queries = getQueriesFromInput();
    const objects = getObjectsFromInput();
    
    if (queries.length === 0) {
        showError('Vui lòng nhập ít nhất một câu query');
        return;
    }
    
    currentQueries = queries;
    currentObjects = objects;
    await performSearch(queries, objects, true);
}

// Handle search more button click
async function handleSearchMore() {
    if (currentQueries.length === 0) {
        showError('Không có query để tìm tiếp');
        return;
    }
    
    await performSearch(currentQueries, currentObjects, false);
}

// Get queries from textarea input
function getQueriesFromInput() {
    const input = queryInput.value.trim();
    if (!input) return [];
    
    return input.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

// Get objects from textarea input
function getObjectsFromInput() {
    const input = objectInput.value.trim();
    if (!input) return [];
    
    return input.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

// Perform search API call
async function performSearch(queries, objects, isNewSearch) {
    try {
        showLoading(true);
        hideError();
        
        const response = await fetch(`${API_BASE_URL}/api/v1/videos/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query_text: queries,
                list_object: objects
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (isNewSearch) {
            currentResults = data.results || [];
            currentPage = 0;
        } else {
            // Append new results to existing ones
            currentResults = [...currentResults, ...(data.results || [])];
        }
        
        displayResults();
        updateButtonStates();
        
    } catch (error) {
        console.error('Search error:', error);
        showError(`Lỗi tìm kiếm: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Display results in grid
function displayResults() {
    if (currentResults.length === 0) {
        resultsSection.style.display = 'none';
        return;
    }
    
    resultsSection.style.display = 'block';
    
    const startIndex = currentPage * ITEMS_PER_PAGE;
    const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, currentResults.length);
    const pageResults = currentResults.slice(startIndex, endIndex);
    
    // Update pagination info
    paginationInfo.textContent = `Hiển thị ${startIndex + 1}-${endIndex} của ${currentResults.length} kết quả`;
    
    // Clear grid
    gridContainer.innerHTML = '';
    
    // Add grid items
    pageResults.forEach(result => {
        const gridItem = createGridItem(result);
        gridContainer.appendChild(gridItem);
    });
    
    // Fill remaining slots with empty items if needed
    const remainingSlots = ITEMS_PER_PAGE - pageResults.length;
    for (let i = 0; i < remainingSlots; i++) {
        const emptyItem = createEmptyGridItem();
        gridContainer.appendChild(emptyItem);
    }
}

// Create a grid item for a result
function createGridItem(result) {
    const gridItem = document.createElement('div');
    gridItem.className = 'grid-item';
    
    const imageUrl = result.jpg_path.startsWith('http') 
        ? result.jpg_path 
        : `${API_BASE_URL}${result.jpg_path}`;
    
    gridItem.innerHTML = `
        <div class="grid-item-image" style="background-image: url('${imageUrl}')" 
             onerror="this.classList.add('error'); this.innerHTML='Không thể tải ảnh';">
        </div>
        <div class="grid-item-info">
            <div class="grid-item-title">${result.original_id}</div>
            <div class="grid-item-score">Độ tương đồng: ${(result.similarity_score * 100).toFixed(1)}%</div>
            <div class="grid-item-frame">Frame: ${result.frame_idx}</div>
        </div>
    `;
    
    return gridItem;
}

// Create an empty grid item
function createEmptyGridItem() {
    const gridItem = document.createElement('div');
    gridItem.className = 'grid-item';
    gridItem.style.opacity = '0.3';
    
    gridItem.innerHTML = `
        <div class="grid-item-image" style="background-color: #f0f0f0;"></div>
        <div class="grid-item-info">
            <div class="grid-item-title">-</div>
            <div class="grid-item-score">-</div>
            <div class="grid-item-frame">-</div>
        </div>
    `;
    
    return gridItem;
}

// Change page
function changePage(direction) {
    const newPage = currentPage + direction;
    const maxPage = Math.ceil(currentResults.length / ITEMS_PER_PAGE) - 1;
    
    if (newPage >= 0 && newPage <= maxPage) {
        currentPage = newPage;
        displayResults();
        updateButtonStates();
    }
}

// Update button states
function updateButtonStates() {
    const maxPage = Math.ceil(currentResults.length / ITEMS_PER_PAGE) - 1;
    
    prevBtn.disabled = currentPage <= 0;
    nextBtn.disabled = currentPage >= maxPage;
    
    searchMoreBtn.disabled = currentQueries.length === 0;
}

// Show/hide loading spinner
function showLoading(show) {
    loadingSpinner.style.display = show ? 'block' : 'none';
    searchBtn.disabled = show;
    searchMoreBtn.disabled = show || currentQueries.length === 0;
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Initialize the app
function init() {
    // Set up some sample data for testing
    queryInput.value = 'a person walking\na person with red hat is walking\ncar driving';
    objectInput.value = 'PERSON\nDOG\nCAR';
    
    // Add keyboard shortcuts
    queryInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            handleSearch();
        }
    });
    
    objectInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            handleSearch();
        }
    });
}

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
