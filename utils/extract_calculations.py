# utils/extract_calculations.py
import json
import numpy as np
import pandas as pd
import logging
from utils.replace_nan_with_string import replace_nan_with_string


logger = logging.getLogger(__name__)


def extract_calculations(df_full, fc_name, timestamp):
    """
    Extract custom data and perform necessary calculations from the downloaded DataFrame,
    then save the results to JSON and Excel files.

    Parameters:
    - df_full (pd.DataFrame): The full DataFrame extracted from Excel.
    - fc_name (str): Fulfillment Center name.
    - timestamp (str): Timestamp string for file naming.
    """
    try:
        logger.info("Extracting calculations and custom data.")

        # Convert 'Paths' column to string to avoid any issues
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

        # Initialize lists to hold extracted data
        extracted_data = []  # For calculations
        rates_data = []      # For rates table
        custom_data = []     # For custom data

        # Custom data extraction specification
        extraction_spec = {
            "Receive Dock": ["Comp TPH"],
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
            "Transfer Out": ["Comp TPH"],
            "Transfer Out Dock": ["Comp TPH"],
            "TO Lead/PA": ["Comp TPH"],
            "TO Problem Solve": ["Comp TPH"]
        }

        # Extract custom data
        for _, record in df_full.iterrows():
            path_name = record.get('Paths')
            if path_name in extraction_spec:
                # Extract the specified fields
                extracted_record = {'Paths': path_name}
                for field in extraction_spec[path_name]:
                    extracted_record[field] = record.get(field)
                custom_data.append(extracted_record)

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
                uph_lp = group_totals['units lp'] / group_totals['h lp'] if group_totals['h lp'] != 0 else None
                uph_op2 = group_totals['units op2'] / group_totals['h op2'] if group_totals['h op2'] != 0 else None

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

                # Add to rates table
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

            else:
                # For single-path groups like 'Pallet Receive', decide whether to include them in rates
                pass  # Assuming we skip them based on your instructions

            # Add an empty row for separation
            extracted_data.append({'Group': '', 'Paths': '', 'units lp': '', 'h lp': '', 'units op2': '', 'h op2': ''})

        # Prepare metadata
        metadata = {
            'fc': fc_name,
            'timestamp': timestamp,
            'report_type': 'kNekro'
        }

        # Create the final data structure
        final_data = {
            'metadata': metadata,
            'data': custom_data,
            'rates': rates_data
        }

        # Define a default converter for JSON serialization that handles NaN values
        def default_converter(o):
            if isinstance(o, float):
                if np.isnan(o):
                    return 'NaN'
                else:
                    return o
            elif isinstance(o, np.integer):
                return int(o)
            elif isinstance(o, np.floating):
                if np.isnan(o):
                    return 'NaN'
                else:
                    return float(o)
            elif isinstance(o, np.ndarray):
                return o.tolist()
            else:
                return o
            
        # Replace NaN in 'custom_data' and 'rates_data'
        final_data['data'] = replace_nan_with_string(final_data['data'])
        final_data['rates'] = replace_nan_with_string(final_data['rates'])

        # Save to JSON
        json_filename = f"kNekro_{fc_name}_{timestamp}.json"
        with open(json_filename, 'w') as json_file:
            json.dump(final_data, json_file, indent=4, default=default_converter)
        logger.info(f"Final data saved to JSON file: {json_filename}")

        # Save to Excel
        excel_filename = f"kNekro_{fc_name}_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_filename) as writer:
            # Custom data to 'Custom Data' sheet
            df_custom = pd.DataFrame(custom_data)
            df_custom.to_excel(writer, sheet_name='Custom Data', index=False)

            # Rates data to 'Rates' sheet
            df_rates = pd.DataFrame(rates_data)
            df_rates.to_excel(writer, sheet_name='Rates', index=False)

            # Extracted data to 'Extracted Data' sheet
            df_extracted = pd.DataFrame(extracted_data)
            df_extracted.to_excel(writer, sheet_name='Extracted Data', index=False)

        logger.info(f"Final data saved to Excel file: {excel_filename}")

    except Exception as e:
        logger.error(f"Error extracting calculations: {e}")
        raise