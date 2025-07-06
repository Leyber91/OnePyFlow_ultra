/**
 * main.js - Core functionality for OnePyFlow Documentation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeSidebar();
    initializeNavigation();
    initializeThemeToggle();
    initializeSearch();
    initializeExpandableElements();
    initializeModal();
    
    // Load architecture diagram
    loadArchitectureDiagram();
});

/**
 * Initialize sidebar functionality
 */
function initializeSidebar() {
    const subnavToggles = document.querySelectorAll('.has-subnav > .nav-link');
    
    subnavToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const parentLi = this.parentElement;
            parentLi.classList.toggle('open');
            
            // If opening this subnav, close others
            if (parentLi.classList.contains('open')) {
                document.querySelectorAll('.has-subnav.open').forEach(item => {
                    if (item !== parentLi) {
                        item.classList.remove('open');
                    }
                });
            }
        });
    });
    
    // Automatically open subnav if a child is active
    const activeSubitem = document.querySelector('.nav-subitem .nav-link.active');
    if (activeSubitem) {
        activeSubitem.closest('.has-subnav').classList.add('open');
    }
}

/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {
                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(section => {
                        section.classList.remove('active');
                    });
                    
                    // Show target section
                    targetSection.classList.add('active');
                    
                    // Update active link
                    document.querySelectorAll('.nav-link').forEach(navLink => {
                        navLink.classList.remove('active');
                    });
                    this.classList.add('active');
                    
                    // Update URL hash
                    window.location.hash = targetId;
                    
                    // Scroll to top if large section
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                    
                    // Store the last visited section in localStorage
                    localStorage.setItem('lastSection', targetId);
                }
            }
        });
    });
    
    // Handle direct URL hash navigation
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        const targetLink = document.querySelector(`.nav-link[href="#${targetId}"]`);
        
        if (targetLink) {
            targetLink.click();
        }
    } else {
        // If no hash, load last visited section or default to overview
        const lastSection = localStorage.getItem('lastSection') || 'overview';
        const lastSectionLink = document.querySelector(`.nav-link[href="#${lastSection}"]`);
        
        if (lastSectionLink) {
            lastSectionLink.click();
        } else {
            // Default to overview if no last section or it doesn't exist
            const overviewLink = document.querySelector('.nav-link[href="#overview"]');
            if (overviewLink) {
                overviewLink.click();
            }
        }
    }
}

/**
 * Initialize theme toggle functionality
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('toggle-theme');
    const themeIcon = themeToggle.querySelector('i');
    const themeText = themeToggle.querySelector('span');
    
    // Check for saved theme preference or respect OS preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        themeText.textContent = 'Light Mode';
    }
    
    // Toggle theme on click
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        let newTheme, newIcon, newText;
        
        if (currentTheme === 'dark') {
            newTheme = 'light';
            newIcon = 'fa-moon';
            newText = 'Dark Mode';
        } else {
            newTheme = 'dark';
            newIcon = 'fa-sun';
            newText = 'Light Mode';
        }
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        themeIcon.className = '';
        themeIcon.classList.add('fas', newIcon);
        themeText.textContent = newText;
    });
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    // Build search index
    let searchIndex = [];
    
    // Index main sections
    document.querySelectorAll('.content-section').forEach(section => {
        const sectionId = section.id;
        const sectionTitle = section.querySelector('h2')?.textContent || '';
        
        searchIndex.push({
            id: sectionId,
            title: sectionTitle,
            content: section.textContent,
            type: 'section'
        });
        
        // Index subsections
        section.querySelectorAll('h3').forEach(subsection => {
            const subsectionId = subsection.id || `${sectionId}-${slugify(subsection.textContent)}`;
            
            if (!subsection.id) {
                subsection.id = subsectionId;
            }
            
            searchIndex.push({
                id: subsectionId,
                title: subsection.textContent,
                content: getSubsectionContent(subsection),
                type: 'subsection',
                parentId: sectionId
            });
        });
        
        // Index code examples
        section.querySelectorAll('.code-block').forEach((codeBlock, index) => {
            const codeId = codeBlock.querySelector('pre code')?.id || `${sectionId}-code-${index}`;
            const codeTitle = codeBlock.closest('.code-example')?.querySelector('h3')?.textContent || 'Code Example';
            
            searchIndex.push({
                id: codeId,
                title: codeTitle,
                content: codeBlock.textContent,
                type: 'code',
                parentId: sectionId
            });
        });
    });
    
    // Handle search input
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        const results = searchIndex.filter(item => {
            return item.title.toLowerCase().includes(query) || 
                   item.content.toLowerCase().includes(query);
        }).slice(0, 10); // Limit to 10 results
        
        if (results.length > 0) {
            searchResults.innerHTML = '';
            
            results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                
                let title = result.title;
                let context = '';
                
                // Find the context around the matched term
                if (result.content.toLowerCase().includes(query)) {
                    const queryIndex = result.content.toLowerCase().indexOf(query);
                    const start = Math.max(queryIndex - 30, 0);
                    const end = Math.min(queryIndex + query.length + 30, result.content.length);
                    const excerpt = result.content.substring(start, end);
                    
                    // Highlight the query term
                    const highlightedExcerpt = excerpt.replace(
                        new RegExp(query, 'gi'),
                        match => `<span class="highlight">${match}</span>`
                    );
                    
                    context = `... ${highlightedExcerpt} ...`;
                }
                
                resultItem.innerHTML = `
                    <div class="result-title">${result.title}</div>
                    ${context ? `<div class="result-context">${context}</div>` : ''}
                    <div class="result-type">${result.type}</div>
                `;
                
                resultItem.addEventListener('click', function() {
                    navigateToResult(result);
                    searchResults.style.display = 'none';
                    searchInput.value = '';
                });
                
                searchResults.appendChild(resultItem);
            });
            
            searchResults.style.display = 'block';
        } else {
            searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
            searchResults.style.display = 'block';
        }
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
    
    // Helper functions
    function slugify(text) {
        return text.toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^\w\-]+/g, '')
            .replace(/\-\-+/g, '-')
            .replace(/^-+/, '')
            .replace(/-+$/, '');
    }
    
    function getSubsectionContent(subsectionEl) {
        let content = '';
        let currentEl = subsectionEl.nextElementSibling;
        
        while (currentEl && !['H2', 'H3'].includes(currentEl.tagName)) {
            content += currentEl.textContent + ' ';
            currentEl = currentEl.nextElementSibling;
        }
        
        return content;
    }
    
    function navigateToResult(result) {
        // Navigate to the correct section first
        const parentId = result.parentId || result.id;
        const sectionLink = document.querySelector(`.nav-link[href="#${parentId}"]`);
        
        if (sectionLink) {
            sectionLink.click();
        }
        
        // Then scroll to the specific element
        setTimeout(() => {
            const element = document.getElementById(result.id);
            
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
                
                // Highlight the element briefly
                element.classList.add('highlight-target');
                setTimeout(() => {
                    element.classList.remove('highlight-target');
                }, 2000);
            }
        }, 100);
    }
}

/**
 * Initialize expandable elements
 */
function initializeExpandableElements() {
    document.querySelectorAll('.expandable-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            content.classList.toggle('show-content');
            
            const icon = this.querySelector('i');
            if (icon) {
                if (content.classList.contains('show-content')) {
                    icon.className = 'fas fa-chevron-up';
                } else {
                    icon.className = 'fas fa-chevron-down';
                }
            }
        });
    });
}

/**
 * Initialize modal functionality
 */
function initializeModal() {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    const closeModal = document.querySelector('.close-modal');
    
    // Close modal when clicking the close button
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Helper function to open modal with content
    window.openModal = function(content) {
        modalBody.innerHTML = content;
        modal.style.display = 'block';
    };
}

/**
 * Load architecture diagram
 * Placeholder for the actual implementation in diagrams.js
 */
function loadArchitectureDiagram() {
    const diagramContainer = document.getElementById('architecture-diagram');
    
    if (diagramContainer) {
        // This will be replaced by the actual implementation in diagrams.js
        diagramContainer.innerHTML = '<div class="diagram-loading">Architecture diagram loading...</div>';
    }
}

/**
 * Module loader system
 */
class ModuleLoader {
    constructor() {
        this.loadedModules = {};
        this.moduleRegistry = {};
    }
    
    /**
     * Register a module with metadata
     */
    registerModule(id, metadata) {
        this.moduleRegistry[id] = metadata;
    }
    
    /**
     * Load module content
     */
    async loadModule(moduleId) {
        if (this.loadedModules[moduleId]) {
            return this.loadedModules[moduleId];
        }
        
        try {
            const response = await fetch(`modules/${moduleId}/documentation.html`);
            
            if (!response.ok) {
                throw new Error(`Failed to load module: ${response.status} ${response.statusText}`);
            }
            
            const content = await response.text();
            this.loadedModules[moduleId] = content;
            
            return content;
        } catch (error) {
            console.error(`Error loading module ${moduleId}:`, error);
            return null;
        }
    }
    
    /**
     * Display module in container
     */
    async displayModule(moduleId, containerId) {
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`Container not found: ${containerId}`);
            return false;
        }
        
        const content = await this.loadModule(moduleId);
        
        if (content) {
            container.innerHTML = content;
            return true;
        }
        
        return false;
    }
}

// Initialize global module loader
window.moduleLoader = new ModuleLoader();
