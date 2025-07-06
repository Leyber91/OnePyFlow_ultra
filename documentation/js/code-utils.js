/**
 * code-utils.js - Utilities for handling code blocks in OnePyFlow Documentation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize code highlighting and copy buttons
    initializeCodeHighlighting();
    initializeCodeCopyButtons();
});

/**
 * Initialize syntax highlighting for code blocks
 */
function initializeCodeHighlighting() {
    // Initialize highlight.js for syntax highlighting
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    // Add line numbers if class 'line-numbers' is present
    document.querySelectorAll('pre.line-numbers code').forEach((block) => {
        addLineNumbers(block);
    });
}

/**
 * Add line numbers to a code block
 */
function addLineNumbers(codeBlock) {
    const lines = codeBlock.innerHTML.split('\n');
    let numberedLines = '';
    
    for (let i = 0; i < lines.length; i++) {
        numberedLines += `<span class="line-number">${i + 1}</span>${lines[i]}\n`;
    }
    
    codeBlock.innerHTML = numberedLines;
    codeBlock.parentElement.classList.add('has-line-numbers');
}

/**
 * Initialize copy buttons for code blocks
 */
function initializeCodeCopyButtons() {
    // Initialize Clipboard.js
    const clipboard = new ClipboardJS('.copy-btn');
    
    // Handle success
    clipboard.on('success', function(e) {
        const button = e.trigger;
        
        // Change button text to show feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        
        // Reset button text after a short delay
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
        
        e.clearSelection();
    });
    
    // Handle errors
    clipboard.on('error', function(e) {
        const button = e.trigger;
        
        // Show error message
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-times"></i> Failed!';
        
        // Reset button text after a short delay
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
        
        console.error('Copy failed:', e.action);
    });
}

/**
 * Create a line highlighting function that can be called from other parts of the app
 */
function highlightCodeLines(codeBlockId, lines) {
    const codeBlock = document.getElementById(codeBlockId);
    
    if (!codeBlock) {
        console.error(`Code block not found: ${codeBlockId}`);
        return;
    }
    
    // Remove existing highlights
    codeBlock.querySelectorAll('.code-highlight').forEach(line => {
        line.classList.remove('code-highlight');
    });
    
    // Process lines argument (can be array, range, or single number)
    let linesToHighlight = [];
    
    if (Array.isArray(lines)) {
        linesToHighlight = lines;
    } else if (typeof lines === 'string' && lines.includes('-')) {
        // Range format: "5-10"
        const [start, end] = lines.split('-').map(num => parseInt(num.trim()));
        for (let i = start; i <= end; i++) {
            linesToHighlight.push(i);
        }
    } else if (typeof lines === 'number') {
        linesToHighlight = [lines];
    }
    
    // Apply highlighting
    linesToHighlight.forEach(lineNum => {
        const lineElement = codeBlock.querySelector(`.line-number:nth-of-type(${lineNum})`);
        if (lineElement) {
            lineElement.parentElement.classList.add('code-highlight');
        }
    });
}

/**
 * Format code blocks with custom options
 */
function formatCodeBlock(codeBlockId, options = {}) {
    const codeBlock = document.getElementById(codeBlockId);
    
    if (!codeBlock) {
        console.error(`Code block not found: ${codeBlockId}`);
        return;
    }
    
    // Apply language formatting
    if (options.language) {
        codeBlock.className = `language-${options.language}`;
        hljs.highlightElement(codeBlock);
    }
    
    // Apply line numbers
    if (options.lineNumbers) {
        codeBlock.parentElement.classList.add('line-numbers');
        addLineNumbers(codeBlock);
    }
    
    // Apply highlighting
    if (options.highlight) {
        highlightCodeLines(codeBlockId, options.highlight);
    }
    
    // Apply title
    if (options.title) {
        const titleElement = document.createElement('div');
        titleElement.className = 'code-title';
        titleElement.textContent = options.title;
        
        codeBlock.parentElement.parentElement.insertBefore(titleElement, codeBlock.parentElement);
    }
    
    // Apply output style
    if (options.isOutput) {
        codeBlock.parentElement.classList.add('code-output');
        
        if (options.outputTitle) {
            const outputTitleElement = document.createElement('div');
            outputTitleElement.className = 'code-output-title';
            outputTitleElement.textContent = options.outputTitle || 'Output';
            
            codeBlock.parentElement.parentElement.insertBefore(outputTitleElement, codeBlock.parentElement);
        }
    }
}

/**
 * Add interactive code tabs
 */
function createCodeTabs(containerId, tabs) {
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return;
    }
    
    // Create the tabs container
    const tabsContainer = document.createElement('div');
    tabsContainer.className = 'code-tabs';
    
    // Create the tab buttons
    const tabButtons = document.createElement('div');
    tabButtons.className = 'code-tab-buttons';
    
    // Create the tab content
    const tabContent = document.createElement('div');
    tabContent.className = 'code-tab-content';
    
    // Create each tab
    tabs.forEach((tab, index) => {
        // Create the button
        const button = document.createElement('button');
        button.className = `code-tab-button ${index === 0 ? 'active' : ''}`;
        button.textContent = tab.title;
        button.setAttribute('data-tab', index);
        tabButtons.appendChild(button);
        
        // Create the content
        const content = document.createElement('div');
        content.className = `code-tab-pane ${index === 0 ? 'active' : ''}`;
        content.setAttribute('data-tab', index);
        
        // Create the code block
        const codeBlock = document.createElement('pre');
        codeBlock.className = `${tab.language ? `language-${tab.language}` : ''}`;
        
        if (tab.lineNumbers) {
            codeBlock.classList.add('line-numbers');
        }
        
        const code = document.createElement('code');
        code.textContent = tab.code;
        code.id = `${containerId}-tab-${index}`;
        
        codeBlock.appendChild(code);
        content.appendChild(codeBlock);
        tabContent.appendChild(content);
    });
    
    // Add event listeners to buttons
    tabButtons.querySelectorAll('.code-tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabIndex = this.getAttribute('data-tab');
            
            // Update active button
            tabButtons.querySelectorAll('.code-tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Update active content
            tabContent.querySelectorAll('.code-tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            tabContent.querySelector(`.code-tab-pane[data-tab="${tabIndex}"]`).classList.add('active');
        });
    });
    
    // Assemble the tabs
    tabsContainer.appendChild(tabButtons);
    tabsContainer.appendChild(tabContent);
    container.appendChild(tabsContainer);
    
    // Apply syntax highlighting
    tabContent.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block);
        
        if (block.parentElement.classList.contains('line-numbers')) {
            addLineNumbers(block);
        }
    });
    
    // Add copy buttons
    tabContent.querySelectorAll('pre').forEach((pre, index) => {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-btn';
        copyButton.setAttribute('data-clipboard-target', `#${containerId}-tab-${index}`);
        copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy';
        pre.appendChild(copyButton);
    });
}

// Make functions globally available
window.highlightCodeLines = highlightCodeLines;
window.formatCodeBlock = formatCodeBlock;
window.createCodeTabs = createCodeTabs;
