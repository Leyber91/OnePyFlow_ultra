
import logging

# Configure logging
logger = logging.getLogger(__name__)



def process_dockflow_data(data):
    """
    Processes DockFlow data to extract workcell information and outbound arcs.
    """
    logger.info("Processing DockFlow data.")
    processed_data = []
    
    # Check for errors in the data
    if 'errors' in data:
        logger.error(f"Errors found in DockFlow data: {data['errors']}")
        raise Exception(f"DockFlow data contains errors: {data['errors']}")
    
    workcells = data.get('data', {}).get('site', {}).get('workcells', [])
    logger.info(f"Number of workcells retrieved: {len(workcells)}")
    
    for idx, workcell in enumerate(workcells, start=1):
        if workcell is None:
            logger.warning(f"Workcell #{idx} is None. Skipping.")
            continue
        
        # Extract workcell details
        workcell_name = workcell.get('id', {}).get('name', '')
        workcell_type = workcell.get('id', {}).get('type', '')
        outbound_arcs = workcell.get('outboundArcs', [])
        
        # Extract outbound arc names
        if outbound_arcs is None:
            outbound_arc_names = []
        else:
            outbound_arc_names = [arc.get('name', '') for arc in outbound_arcs if arc is not None]
        
        # Construct the row
        row = [workcell_name, workcell_type] + outbound_arc_names
        processed_data.append(row)
    
    logger.info("DockFlow data processing complete.")
    return processed_data