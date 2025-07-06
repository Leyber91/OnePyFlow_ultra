import logging
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

def handle_nan_for_json(obj):
    """
    Recursively replace NaN values with empty strings in a nested structure (dict, list, etc.)
    to ensure proper JSON serialization.
    
    Args:
        obj: Any Python object that might contain NaN values
        
    Returns:
        The same object with NaN values replaced by empty strings
    """
    if isinstance(obj, dict):
        return {k: handle_nan_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_for_json(item) for item in obj]
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return handle_nan_for_json(obj.to_dict())
    elif isinstance(obj, (float, np.float64, np.float32)) and np.isnan(obj):
        return ""
    elif pd.isna(obj):  # Catch any other pandas NA types
        return ""
    else:
        return obj

def process_necronomicon_data(df_full, fc_name):
    """
    Processes the Necronomicon data, performing calculations and preparing data for output.
    
    Parameters:
    - df_full (pd.DataFrame): The full DataFrame containing Necronomicon data.
    - fc_name (str): The name of the facility or relevant identifier.
    
    Returns:
    - dict: A dictionary containing processed DataFrames for 'extracted_data', 'rates_data', and 'custom_data'.
    """
    try:
        # Ensure 'Paths' column is string
        if 'Paths' not in df_full.columns:
            logger.error("[NECRO] Missing 'Paths' column in input DataFrame")
            return None
            
        df_full['Paths'] = df_full['Paths'].astype(str)
        
        # Define the paths and groups for calculations
        groups = {
            'Each Receive': [
                'Each Receive - Small',
                'Each Receive - Medium',
                'Each Receive - Large'
            ],
            'Prep Recorder': [
                'Prep Recorder - Small',
                'Prep Recorder - Medium',
                'Prep Recorder - Large',
                'Prep Recorder - Heavy/Bulky'
            ],
            'Pallet Receive': [
                'Pallet Receive'
            ],
            'Manual Sort': [
                'RC Sort - Small',
                'RC Sort - Medium',
                'RC Sort - Large',
                'RC Sort - Heavy/Bulky'
            ]
        }

        # Custom data extraction specification - includes all fields from original output
        extraction_spec = {
            "THROUGHPUT": ["Base TPH"],
            "FCSummary - Inbound": ["Base Volume", "Comp Volume", "Comp Hours", "Comp TPH"],
            "FCSummary - DA": ["Base Volume", "Comp Volume", "Comp Hours", "Comp TPH"],
            "Receive Dock": ["Comp TPH", "Comp Volume", "Comp Hours"],  # Added Volume and Hours
            "Each Receive - Small": ["Comp Volume", "Comp Hours"],
            "Each Receive - Medium": ["Comp Volume", "Comp Hours"],
            "Each Receive - Large": ["Comp Volume", "Comp Hours"],
            "Case Receive": ["Comp TPH"],
            "LP Receive": ["Comp TPH"],
            "Pallet Receive": ["Comp TPH"],
            "Receive Support": ["Comp TPH"],
            "Cubiscan": ["Comp TPH"],
            "Prep Recorder - Small": ["Comp Volume", "Comp Hours"],
            "Prep Recorder - Medium": ["Comp Volume", "Comp Hours"],
            "Prep Recorder - Large": ["Comp Volume", "Comp Hours"],
            "Prep Recorder - Heavy/Bulky": ["Comp Volume", "Comp Hours"],
            "Prep Support": ["Comp TPH"],
            "RSR Support": ["Comp TPH"],
            "IB Lead/PA": ["Comp TPH"],
            "IB Problem Solve": ["Comp TPH"],
            "RC Sort - Small": ["Base Volume", "Comp Volume", "Comp Hours"],
            "RC Sort - Medium": ["Base Volume", "Comp Volume", "Comp Hours"],
            "RC Sort - Large": ["Base Volume", "Comp Volume", "Comp Hours"],
            "RC Sort - Heavy/Bulky": ["Base Volume", "Comp Volume", "Comp Hours"],
            "Transfer Out": ["Comp TPH", "Comp Volume", "Comp Hours"],  # Added Volume and Hours
            "Transfer Out Dock": ["Comp TPH"],
            "TO Lead/PA": ["Comp TPH"],
            "TO Problem Solve": ["Comp TPH"]
        }

        # Inbound paths list - used to identify inbound records for hours calculation
        inbound_paths = [
            'Each Receive - Small', 
            'Each Receive - Medium', 
            'Each Receive - Large',
            'Each Receive - Heavy/Bulky',
            'Prep Recorder - Small', 
            'Prep Recorder - Medium', 
            'Prep Recorder - Large',
            'Prep Recorder - Heavy/Bulky', 
            'Pallet Receive', 
            'Case Receive', 
            'LP Receive',
            'Receive Dock', 
            'Receive Support', 
            'Cubiscan', 
            'IB Lead/PA', 
            'IB Problem Solve',
            'Prep Support', 
            'RSR Support'
        ]
        
        # DA paths list - used to identify DA records for hours calculation
        da_paths = [
            'RC Sort - Small', 
            'RC Sort - Medium', 
            'RC Sort - Large', 
            'RC Sort - Heavy/Bulky',
            'Transfer Out', 
            'Transfer Out Dock', 
            'TO Lead/PA', 
            'TO Problem Solve'
        ]

        # Calculate the total Inbound hours by summing the hours for all Inbound paths
        total_inbound_hours = 0
        for path in inbound_paths:
            path_df = df_full[df_full['Paths'] == path]
            if not path_df.empty:
                for _, row in path_df.iterrows():
                    if 'Comp Hours' in row and pd.notna(row['Comp Hours']):
                        total_inbound_hours += float(row['Comp Hours'])
        
        logger.info(f"[NECRO] Calculated total Inbound hours: {total_inbound_hours}")

        # Calculate the total DA hours by summing the hours for all DA paths
        total_da_hours = 0
        for path in da_paths:
            path_df = df_full[df_full['Paths'] == path]
            if not path_df.empty:
                for _, row in path_df.iterrows():
                    if 'Comp Hours' in row and pd.notna(row['Comp Hours']):
                        total_da_hours += float(row['Comp Hours'])
        
        logger.info(f"[NECRO] Calculated total DA hours: {total_da_hours}")

        # Initialize lists to hold extracted data
        extracted_data = []  # For calculations
        rates_data = []      # For rates table
        custom_data = []     # For custom data

        # Extract raw data from Receive Dock and Transfer Out for later use in FCSummary
        receive_dock_row = None
        transfer_out_row = None
        
        for _, record in df_full.iterrows():
            path_name = record.get('Paths')
            
            # Capture raw data for summary calculations
            if path_name == 'Receive Dock':
                receive_dock_row = record
            elif path_name == 'Transfer Out':
                transfer_out_row = record
                
            # Extract data for all paths in extraction_spec
            if path_name in extraction_spec:
                # Initialize the extracted record with 'Paths'
                extracted_record = {'Paths': path_name}
                for field in extraction_spec[path_name]:
                    if field in record:
                        value = record.get(field)
                        if pd.notna(value):
                            extracted_record[field] = value
                # Append only if there are additional fields beyond 'Paths'
                if len(extracted_record) > 1:
                    custom_data.append(extracted_record)
                else:
                    # Optionally, include 'Paths' even if no additional fields
                    custom_data.append(extracted_record)

        # Fill in missing fields in custom_data with zeros
        for item in custom_data:
            path = item['Paths']
            if path in extraction_spec:
                for field in extraction_spec[path]:
                    if field not in item:
                        item[field] = 0.0
        
        # Manually create or update FCSummary entries using the raw data and calculated total hours
        # FCSummary - Inbound
        if receive_dock_row is not None and 'Comp Volume' in receive_dock_row and 'Comp Hours' in receive_dock_row:
            inbound_volume = float(receive_dock_row.get('Comp Volume', 0))
            # Use the calculated total hours for all Inbound paths
            inbound_hours = total_inbound_hours
            inbound_tph = inbound_volume / inbound_hours if inbound_hours > 0 else 0
            
            # Look for existing FCSummary - Inbound entry to update
            inbound_summary_found = False
            for item in custom_data:
                if item['Paths'] == 'FCSummary - Inbound':
                    item['Base Volume'] = inbound_volume
                    item['Comp Volume'] = inbound_volume
                    item['Comp Hours'] = inbound_hours
                    item['Comp TPH'] = inbound_tph
                    inbound_summary_found = True
                    break
            
            # If not found, create a new entry
            if not inbound_summary_found:
                custom_data.append({
                    'Paths': 'FCSummary - Inbound',
                    'Base Volume': inbound_volume,
                    'Comp Volume': inbound_volume,
                    'Comp Hours': inbound_hours,
                    'Comp TPH': inbound_tph
                })
            
            logger.info(f"[NECRO] Using calculated total Inbound hours for Inbound Summary: Volume={inbound_volume}, Hours={inbound_hours}")
        else:
            # Fallback to hardcoded values for volume, but use calculated hours
            logger.warning("[NECRO] Receive Dock data not found for FCSummary - Inbound, using fallback values for volume but calculated hours")
            
            # Default fallback volume (use actual data or a reasonable estimate)
            fallback_volume = 8015637.3  # Example value
            
            # Look for existing FCSummary - Inbound entry to update
            inbound_summary_found = False
            for item in custom_data:
                if item['Paths'] == 'FCSummary - Inbound':
                    item['Base Volume'] = fallback_volume
                    item['Comp Volume'] = fallback_volume
                    item['Comp Hours'] = total_inbound_hours
                    item['Comp TPH'] = fallback_volume / total_inbound_hours if total_inbound_hours > 0 else 0
                    inbound_summary_found = True
                    break
            
            # If not found, create a new entry
            if not inbound_summary_found:
                custom_data.append({
                    'Paths': 'FCSummary - Inbound',
                    'Base Volume': fallback_volume,
                    'Comp Volume': fallback_volume,
                    'Comp Hours': total_inbound_hours,
                    'Comp TPH': fallback_volume / total_inbound_hours if total_inbound_hours > 0 else 0
                })
        
        # FCSummary - DA
        if transfer_out_row is not None and 'Comp Volume' in transfer_out_row and 'Comp Hours' in transfer_out_row:
            da_volume = float(transfer_out_row.get('Comp Volume', 0))
            # Use the calculated total hours for all DA paths
            da_hours = total_da_hours
            da_tph = da_volume / da_hours if da_hours > 0 else 0
            
            # Look for existing FCSummary - DA entry to update
            da_summary_found = False
            for item in custom_data:
                if item['Paths'] == 'FCSummary - DA':
                    item['Base Volume'] = da_volume
                    item['Comp Volume'] = da_volume
                    item['Comp Hours'] = da_hours
                    item['Comp TPH'] = da_tph
                    da_summary_found = True
                    break
            
            # If not found, create a new entry
            if not da_summary_found:
                custom_data.append({
                    'Paths': 'FCSummary - DA',
                    'Base Volume': da_volume,
                    'Comp Volume': da_volume,
                    'Comp Hours': da_hours,
                    'Comp TPH': da_tph
                })
            
            logger.info(f"[NECRO] Using calculated total DA hours for DA Summary: Volume={da_volume}, Hours={da_hours}")
        else:
            # Fallback to hardcoded values for volume, but use calculated hours
            logger.warning("[NECRO] Transfer Out data not found for FCSummary - DA, using fallback values for volume but calculated hours")
            
            # Default fallback volume (use actual data or a reasonable estimate)
            fallback_volume = 8015637.3  # Example value
            
            # Look for existing FCSummary - DA entry to update
            da_summary_found = False
            for item in custom_data:
                if item['Paths'] == 'FCSummary - DA':
                    item['Base Volume'] = fallback_volume
                    item['Comp Volume'] = fallback_volume
                    item['Comp Hours'] = total_da_hours
                    item['Comp TPH'] = fallback_volume / total_da_hours if total_da_hours > 0 else 0
                    da_summary_found = True
                    break
            
            # If not found, create a new entry
            if not da_summary_found:
                custom_data.append({
                    'Paths': 'FCSummary - DA',
                    'Base Volume': fallback_volume,
                    'Comp Volume': fallback_volume,
                    'Comp Hours': total_da_hours,
                    'Comp TPH': fallback_volume / total_da_hours if total_da_hours > 0 else 0
                })

        # Perform calculations and rates extraction
        for group_name, paths in groups.items():
            group_data = []
            for path in paths:
                # Filter the DataFrame for the current path
                df_path = df_full[df_full['Paths'] == path]
                if not df_path.empty:
                    record = df_path.iloc[0]
                    extracted_record = {
                        'Group': group_name,
                        'Paths': path,
                        'units lp': float(record.get('Base Volume', 0)),
                        'h lp': float(record.get('Base Hours', 0)),
                        'units op2': float(record.get('Comp Volume', 0)),
                        'h op2': float(record.get('Comp Hours', 0))
                    }
                    group_data.append(extracted_record)
                else:
                    # If path not found, add zeros
                    extracted_record = {
                        'Group': group_name,
                        'Paths': path,
                        'units lp': 0.0,
                        'h lp': 0.0,
                        'units op2': 0.0,
                        'h op2': 0.0
                    }
                    group_data.append(extracted_record)

            # Append individual path data to extracted_data
            extracted_data.extend(group_data)

            # Calculate totals for the group if more than one path
            if len(paths) > 1:
                group_totals = {
                    'Group': f"{group_name} Total",
                    'Paths': '',
                    'units lp': float(sum(item['units lp'] for item in group_data)),
                    'h lp': float(sum(item['h lp'] for item in group_data)),
                    'units op2': float(sum(item['units op2'] for item in group_data)),
                    'h op2': float(sum(item['h op2'] for item in group_data))
                }
                # Append group totals to extracted_data
                extracted_data.append(group_totals)

                # Compute additional calculations
                uph_lp = group_totals['units lp'] / group_totals['h lp'] if group_totals['h lp'] != 0 else 0
                uph_op2 = group_totals['units op2'] / group_totals['h op2'] if group_totals['h op2'] != 0 else 0

                # Append the calculations
                calculation_row = {
                    'Group': '',
                    'Paths': '',
                    'units lp': 'UPH lp',
                    'h lp': uph_lp,
                    'units op2': 'UPH op2',
                    'h op2': uph_op2
                }
                extracted_data.append(calculation_row)

                # Append to rates table
                rates_row = {
                    'Rates': group_name,
                    'LP': uph_lp,
                    'OP2': uph_op2
                }
                rates_data.append(rates_row)

                # Check if group_name is 'Prep Recorder' to add 'Prep Pallet' row
                if group_name == 'Prep Recorder':
                    # Add 'Prep Pallet' with same values as 'Prep Recorder'
                    prep_pallet_row = {
                        'Rates': 'Prep Pallet',
                        'LP': uph_lp,
                        'OP2': uph_op2
                    }
                    rates_data.append(prep_pallet_row)

            # Add an empty row for separation
            extracted_data.append({'Group': '', 'Paths': '', 'units lp': '', 'h lp': '', 'units op2': '', 'h op2': ''})

        # Prepare data frames for output
        df_extracted = pd.DataFrame(extracted_data)
        df_rates = pd.DataFrame(rates_data)
        
        # Fill NaN values with empty strings before conversion
        df_extracted = df_extracted.fillna("") if not df_extracted.empty else df_extracted
        df_rates = df_rates.fillna("") if not df_rates.empty else df_rates
        
        # Convert DataFrames to serializable formats
        extracted_data_serializable = df_extracted.to_dict(orient='records') if not df_extracted.empty else []
        rates_data_serializable = df_rates.to_dict(orient='records') if not df_rates.empty else []

        # Prepare data dict to return
        processed_data = {
            'extracted_data': extracted_data_serializable,
            'rates_data': rates_data_serializable,
            'custom_data': custom_data  # Already a list of dicts
        }

        logger.info(f"[NECRO] Successfully processed data: {len(custom_data)} custom items, {len(extracted_data_serializable)} extracted records, {len(rates_data_serializable)} rate records")
        return processed_data

    except Exception as e:
        logger.error(f"Error processing Necronomicon data: {e}", exc_info=True)
        return None