/**
 * diagrams.js - Interactive diagrams for OnePyFlow Documentation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the architecture diagram
    initializeArchitectureDiagram();
});

/**
 * Initialize the interactive architecture diagram
 */
function initializeArchitectureDiagram() {
    const diagramContainer = document.getElementById('architecture-diagram');
    
    if (!diagramContainer) {
        return;
    }
    
    // Define the module data for the architecture diagram
    const moduleData = {
        // Core modules
        'oneflow': {
            id: 'oneflow',
            title: 'oneflow.py',
            description: 'Main orchestration module',
            type: 'core',
            position: { x: 50, y: 50 },
            width: 180,
            height: 80
        },
        'oneflow_audit': {
            id: 'oneflow_audit',
            title: 'oneflow_audit.py',
            description: 'Execution tracking & audit logging',
            type: 'core',
            position: { x: 50, y: 150 },
            width: 180,
            height: 80
        },
        'oneflow_concurrency': {
            id: 'oneflow_concurrency',
            title: 'oneflow_concurrency.py',
            description: 'Concurrent task execution',
            type: 'core',
            position: { x: 50, y: 250 },
            width: 180,
            height: 80
        },
        'oneflow_data_sources': {
            id: 'oneflow_data_sources',
            title: 'oneflow_data_sources.py',
            description: 'Data source configuration',
            type: 'core',
            position: { x: 50, y: 350 },
            width: 180,
            height: 80
        },
        
        // Data retrieval modules
        'data_retrieval': {
            id: 'data_retrieval',
            title: 'data_retrieval.py',
            description: 'Data retrieval orchestration',
            type: 'retrieval',
            position: { x: 300, y: 100 },
            width: 180,
            height: 80
        },
        'pull_dock_master': {
            id: 'pull_dock_master',
            title: 'pull_dock_master.py',
            description: 'DockMaster data retrieval',
            type: 'retrieval',
            position: { x: 300, y: 200 },
            width: 180,
            height: 80
        },
        'pull_galaxy': {
            id: 'pull_galaxy',
            title: 'pull_galaxy.py',
            description: 'Galaxy data retrieval',
            type: 'retrieval',
            position: { x: 300, y: 300 },
            width: 180,
            height: 80
        },
        
        // Data processing modules
        'data_processing': {
            id: 'data_processing',
            title: 'data_processing.py',
            description: 'Data processing orchestration',
            type: 'processing',
            position: { x: 550, y: 100 },
            width: 180,
            height: 80
        },
        'process_dock_master_data': {
            id: 'process_dock_master_data',
            title: 'process_dock_master_data.py',
            description: 'DockMaster data processing',
            type: 'processing',
            position: { x: 550, y: 200 },
            width: 180,
            height: 80
        },
        'process_galaxy_data': {
            id: 'process_galaxy_data',
            title: 'process_galaxy_data.py',
            description: 'Galaxy data processing',
            type: 'processing',
            position: { x: 550, y: 300 },
            width: 180,
            height: 80
        },
        
        // Feature modules
        'ppr_module': {
            id: 'ppr_module',
            title: 'PPR Module',
            description: 'Process Performance Reports',
            type: 'feature',
            position: { x: 800, y: 50 },
            width: 180,
            height: 80
        },
        'yms_module': {
            id: 'yms_module',
            title: 'YMS Module',
            description: 'Yard Management System',
            type: 'feature',
            position: { x: 800, y: 150 },
            width: 180,
            height: 80
        },
        'fmc_module': {
            id: 'fmc_module',
            title: 'FMC Module',
            description: 'FMC Integration',
            type: 'feature',
            position: { x: 800, y: 250 },
            width: 180,
            height: 80
        },
        'alps_module': {
            id: 'alps_module',
            title: 'ALPS Module',
            description: 'ALPS Integration',
            type: 'feature',
            position: { x: 800, y: 350 },
            width: 180,
            height: 80
        },
        
        // Utility modules
        'authenticate': {
            id: 'authenticate',
            title: 'authenticate.py',
            description: 'Authentication utilities',
            type: 'utility',
            position: { x: 300, y: 450 },
            width: 180,
            height: 80
        },
        'utils': {
            id: 'utils',
            title: 'utils.py',
            description: 'Common utilities',
            type: 'utility',
            position: { x: 550, y: 450 },
            width: 180,
            height: 80
        },
        
        // GUI modules
        'oneflow_gui': {
            id: 'oneflow_gui',
            title: 'oneflow_gui.py',
            description: 'GUI interface',
            type: 'gui',
            position: { x: 800, y: 450 },
            width: 180,
            height: 80
        }
    };
    
    // Define the connections between modules
    const connections = [
        // Core module connections
        { source: 'oneflow', target: 'oneflow_audit', label: 'uses' },
        { source: 'oneflow', target: 'oneflow_concurrency', label: 'uses' },
        { source: 'oneflow', target: 'oneflow_data_sources', label: 'uses' },
        { source: 'oneflow', target: 'data_retrieval', label: 'calls' },
        { source: 'oneflow', target: 'data_processing', label: 'calls' },
        
        // Data retrieval connections
        { source: 'data_retrieval', target: 'pull_dock_master', label: 'calls' },
        { source: 'data_retrieval', target: 'pull_galaxy', label: 'calls' },
        { source: 'data_retrieval', target: 'authenticate', label: 'uses' },
        
        // Data processing connections
        { source: 'data_processing', target: 'process_dock_master_data', label: 'calls' },
        { source: 'data_processing', target: 'process_galaxy_data', label: 'calls' },
        
        // Feature module connections
        { source: 'oneflow', target: 'ppr_module', label: 'integrates' },
        { source: 'oneflow', target: 'yms_module', label: 'integrates' },
        { source: 'oneflow', target: 'fmc_module', label: 'integrates' },
        { source: 'oneflow', target: 'alps_module', label: 'integrates' },
        
        // GUI connections
        { source: 'oneflow_gui', target: 'oneflow', label: 'calls' }
    ];
    
    // Define module groups
    const moduleGroups = [
        { 
            id: 'core-group', 
            title: 'Core Modules', 
            modules: ['oneflow', 'oneflow_audit', 'oneflow_concurrency', 'oneflow_data_sources'],
            position: { x: 30, y: 30 },
            width: 220,
            height: 420
        },
        { 
            id: 'retrieval-group', 
            title: 'Data Retrieval', 
            modules: ['data_retrieval', 'pull_dock_master', 'pull_galaxy'],
            position: { x: 280, y: 80 },
            width: 220,
            height: 320
        },
        { 
            id: 'processing-group', 
            title: 'Data Processing', 
            modules: ['data_processing', 'process_dock_master_data', 'process_galaxy_data'],
            position: { x: 530, y: 80 },
            width: 220,
            height: 320
        },
        { 
            id: 'feature-group', 
            title: 'Feature Modules', 
            modules: ['ppr_module', 'yms_module', 'fmc_module', 'alps_module'],
            position: { x: 780, y: 30 },
            width: 220,
            height: 420
        },
        { 
            id: 'utility-group', 
            title: 'Utilities', 
            modules: ['authenticate', 'utils'],
            position: { x: 280, y: 430 },
            width: 470,
            height: 100
        }
    ];
    
    // Create the diagram
    createArchitectureDiagram(diagramContainer, moduleData, connections, moduleGroups);
}

/**
 * Create the architecture diagram
 */
function createArchitectureDiagram(container, modules, connections, groups) {
    // Clear the container
    container.innerHTML = '';
    
    // Create the architecture container
    const architectureContainer = document.createElement('div');
    architectureContainer.className = 'architecture-container';
    container.appendChild(architectureContainer);
    
    // Create module groups
    groups.forEach(group => {
        const groupElement = document.createElement('div');
        groupElement.className = 'module-group';
        groupElement.id = group.id;
        groupElement.style.left = `${group.position.x}px`;
        groupElement.style.top = `${group.position.y}px`;
        groupElement.style.width = `${group.width}px`;
        groupElement.style.height = `${group.height}px`;
        
        const groupLabel = document.createElement('div');
        groupLabel.className = 'group-label';
        groupLabel.textContent = group.title;
        groupElement.appendChild(groupLabel);
        
        architectureContainer.appendChild(groupElement);
    });
    
    // Create SVG for connections
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.zIndex = '5';
    architectureContainer.appendChild(svg);
    
    // Create module nodes
    Object.values(modules).forEach(module => {
        const moduleNode = document.createElement('div');
        moduleNode.className = `module-node module-${module.type}`;
        moduleNode.id = `module-${module.id}`;
        moduleNode.style.left = `${module.position.x}px`;
        moduleNode.style.top = `${module.position.y}px`;
        moduleNode.style.width = `${module.width}px`;
        
        const moduleTitle = document.createElement('div');
        moduleTitle.className = 'module-title';
        moduleTitle.textContent = module.title;
        moduleNode.appendChild(moduleTitle);
        
        const moduleDescription = document.createElement('div');
        moduleDescription.className = 'module-description';
        moduleDescription.textContent = module.description;
        moduleNode.appendChild(moduleDescription);
        
        // Add click event to highlight connections
        moduleNode.addEventListener('click', function() {
            highlightConnections(module.id);
        });
        
        architectureContainer.appendChild(moduleNode);
    });
    
    // Create connections
    connections.forEach((connection, index) => {
        drawConnection(svg, modules[connection.source], modules[connection.target], connection.label, index);
    });
    
    // Add interactive controls
    addInteractiveControls(container, modules, connections);
    
    // Add diagram legend
    addDiagramLegend(container);
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'diagram-tooltip';
    architectureContainer.appendChild(tooltip);
    
    // Add tooltip functionality
    addTooltipFunctionality(tooltip, modules);
}

/**
 * Draw a connection between two modules
 */
function drawConnection(svg, sourceModule, targetModule, label, index) {
    if (!sourceModule || !targetModule) {
        console.error('Source or target module missing');
        return;
    }
    
    // Calculate connection points
    const sourceX = sourceModule.position.x + sourceModule.width / 2;
    const sourceY = sourceModule.position.y + sourceModule.height / 2;
    const targetX = targetModule.position.x + targetModule.width / 2;
    const targetY = targetModule.position.y + targetModule.height / 2;
    
    // Create the connection path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'connection-line');
    path.setAttribute('id', `connection-${index}`);
    path.setAttribute('data-source', sourceModule.id);
    path.setAttribute('data-target', targetModule.id);
    
    // Create a curved path
    const dx = targetX - sourceX;
    const dy = targetY - sourceY;
    const dr = Math.sqrt(dx * dx + dy * dy);
    
    path.setAttribute('d', `M${sourceX},${sourceY} A${dr},${dr} 0 0,1 ${targetX},${targetY}`);
    
    svg.appendChild(path);
    
    // Add a label
    if (label) {
        const textPath = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textPath.setAttribute('class', 'connection-label');
        
        // Position the label at the midpoint of the connection
        const midX = (sourceX + targetX) / 2;
        const midY = (sourceY + targetY) / 2 - 10; // Offset slightly
        textPath.setAttribute('x', midX);
        textPath.setAttribute('y', midY);
        
        textPath.textContent = label;
        svg.appendChild(textPath);
    }
}

/**
 * Highlight connections related to a module
 */
function highlightConnections(moduleId) {
    // Reset all modules and connections
    document.querySelectorAll('.module-node').forEach(node => {
        node.classList.remove('active');
    });
    
    document.querySelectorAll('.connection-line').forEach(connection => {
        connection.classList.remove('active');
    });
    
    // Highlight the selected module
    const selectedModule = document.getElementById(`module-${moduleId}`);
    if (selectedModule) {
        selectedModule.classList.add('active');
    }
    
    // Highlight direct connections
    document.querySelectorAll('.connection-line').forEach(connection => {
        const source = connection.getAttribute('data-source');
        const target = connection.getAttribute('data-target');
        
        if (source === moduleId || target === moduleId) {
            connection.classList.add('active');
            
            // Also highlight connected modules
            if (source === moduleId) {
                const targetModule = document.getElementById(`module-${target}`);
                if (targetModule) {
                    targetModule.classList.add('active');
                }
            }
            
            if (target === moduleId) {
                const sourceModule = document.getElementById(`module-${source}`);
                if (sourceModule) {
                    sourceModule.classList.add('active');
                }
            }
        }
    });
}

/**
 * Add interactive controls to the diagram
 */
function addInteractiveControls(container, modules, connections) {
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'interactive-controls';
    
    // Create control buttons for module types
    const moduleTypes = ['all', 'core', 'retrieval', 'processing', 'feature', 'utility', 'gui'];
    
    moduleTypes.forEach(type => {
        const button = document.createElement('button');
        button.className = 'control-button';
        button.setAttribute('data-type', type);
        button.textContent = type === 'all' ? 'All Modules' : `${type.charAt(0).toUpperCase() + type.slice(1)} Modules`;
        
        button.addEventListener('click', function() {
            // Update button states
            document.querySelectorAll('.control-button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Show/hide modules based on type
            Object.values(modules).forEach(module => {
                const moduleElement = document.getElementById(`module-${module.id}`);
                
                if (type === 'all' || module.type === type) {
                    moduleElement.style.display = 'block';
                } else {
                    moduleElement.style.display = 'none';
                }
            });
            
            // Show/hide connections based on visible modules
            document.querySelectorAll('.connection-line').forEach(connection => {
                const source = connection.getAttribute('data-source');
                const target = connection.getAttribute('data-target');
                
                const sourceModule = document.getElementById(`module-${source}`);
                const targetModule = document.getElementById(`module-${target}`);
                
                if (sourceModule && targetModule && 
                    sourceModule.style.display !== 'none' && 
                    targetModule.style.display !== 'none') {
                    connection.style.display = 'block';
                } else {
                    connection.style.display = 'none';
                }
            });
        });
        
        controlsContainer.appendChild(button);
    });
    
    // Set "All Modules" as active by default
    controlsContainer.querySelector('[data-type="all"]').classList.add('active');
    
    // Add controls before the diagram
    container.insertBefore(controlsContainer, container.firstChild);
}

/**
 * Add a legend to the diagram
 */
function addDiagramLegend(container) {
    const legend = document.createElement('div');
    legend.className = 'diagram-legend';
    
    const legendItems = [
        { type: 'core', label: 'Core Modules' },
        { type: 'retrieval', label: 'Data Retrieval' },
        { type: 'processing', label: 'Data Processing' },
        { type: 'feature', label: 'Feature Modules' },
        { type: 'utility', label: 'Utilities' }
    ];
    
    legendItems.forEach(item => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        
        const colorBox = document.createElement('div');
        colorBox.className = `legend-color legend-${item.type}`;
        
        const label = document.createElement('span');
        label.textContent = item.label;
        
        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legend.appendChild(legendItem);
    });
    
    container.appendChild(legend);
}

/**
 * Add tooltip functionality to the diagram
 */
function addTooltipFunctionality(tooltip, modules) {
    // Add mouseover event to module nodes
    document.querySelectorAll('.module-node').forEach(node => {
        node.addEventListener('mouseover', function() {
            const moduleId = this.id.replace('module-', '');
            const module = modules[moduleId];
            
            if (module) {
                tooltip.innerHTML = `
                    <div class="tooltip-title">${module.title}</div>
                    <div class="tooltip-content">${module.description}</div>
                `;
                
                const rect = this.getBoundingClientRect();
                const container = this.closest('.architecture-container');
                const containerRect = container.getBoundingClientRect();
                
                tooltip.style.left = `${rect.right - containerRect.left + 10}px`;
                tooltip.style.top = `${rect.top - containerRect.top}px`;
                tooltip.classList.add('visible');
            }
        });
        
        node.addEventListener('mouseout', function() {
            tooltip.classList.remove('visible');
        });
    });
}
