#!/usr/bin/env python3
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)

def _fix_nan_in_dict(d):
    """Replace any Pandas-null value (NaN/None) with the string "NaN"."""
    new_dict = {}
    for k, v in d.items():
        if pd.isnull(v):
            new_dict[k] = "NaN"
        else:
            new_dict[k] = v
    return new_dict

def _fix_nan_in_list_of_dicts(list_of_dicts):
    """Apply _fix_nan_in_dict to each dict in a list."""
    return [_fix_nan_in_dict(item) for item in list_of_dicts]

def _fix_nan_in_summary(summary_dict):
    """Apply _fix_nan_in_dict to a single summary dict (if present)."""
    return _fix_nan_in_dict(summary_dict) if summary_dict else {}

def process_icqa_data(csv_path):
    """
    Processes the ICQA CSV data in three ways:
      1) Unaggregated data (row-by-row).
      2) Aggregated data by destination_warehouse (icqa_aggregated).
         - Summations by container_type => UPC, UPT, UPP.
      3) A summary dictionary (global sums, global ratios, row-by-row averages).

    Returns a tuple: (icqa_unaggregated, icqa_aggregated, icqa_summary).

    Debugging enhancements:
      - Print CSV columns, row count, and sample data to the logs.
      - Write the full DataFrame to 'icqa_data.txt' for deeper inspection.
      - Log unique values for c1_container_type.
      - Log shape info after group/pivot operations.
    """
    # --- 1) Read the CSV
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"[ICQA PROCESS] Successfully read CSV from: {csv_path}")
        logger.info(f"[ICQA PROCESS] Row count: {len(df)}")
        logger.debug(f"[ICQA PROCESS] Columns: {df.columns.tolist()}")

        # Show a small sample in the logs:
        logger.debug(f"[ICQA PROCESS] Sample data:\n{df.head(5)}")

        # Optionally, check if c1_container_type is present, then list its unique values
        if "c1_container_type" in df.columns:
            unique_ctypes = df["c1_container_type"].unique()
            logger.debug(f"[ICQA PROCESS] Unique c1_container_type values: {unique_ctypes}")
        else:
            logger.debug("[ICQA PROCESS] 'c1_container_type' column not found in CSV.")

        # Write entire DataFrame to a text file for offline inspection
        ##with open('icqa_data.txt', 'w', encoding='utf-8') as file:
        ##    file.write(df.to_string())

    except Exception as e:
        logger.error(f"[ICQA PROCESS] Error reading CSV data: {e}", exc_info=True)
        # Return empty structures if read fails
        return [], [], {}

    # --- PART A: Build unaggregated data
    icqa_unaggregated = []
    try:
        for _, row in df.iterrows():
            icqa_unaggregated.append({
                "source_warehouse":       row.get("source_warehouse_id", None),
                "destination_warehouse":  row.get("destination_warehouse_id", None),
                # If c1_container_type is consistently NaN, you may switch to "container_type"
                "container_type":         row.get("container_type", None),
                "sum_units":              row.get("sum_units", None),
                "container_count":        row.get("container_count", None),
                "c1_container_count":     row.get("c1_container_count", None)
            })

        logger.info(f"[ICQA PROCESS] Unaggregated data built. Record count = {len(icqa_unaggregated)}")
    except Exception as e:
        logger.error(f"[ICQA PROCESS] Error building unaggregated data: {e}", exc_info=True)

    # --- PART B: Aggregation
    icqa_aggregated = []
    try:
        # Group by warehouse + c1_container_type
        grouped = (
            df
            .groupby(["destination_warehouse_id", "container_type"], as_index=False)
            .agg({"sum_units": "sum", "container_count": "sum"})
        )
        logger.debug(f"[ICQA PROCESS] groupby shape = {grouped.shape}")
        logger.debug(f"[ICQA PROCESS] groupby sample:\n{grouped.head(5)}")

        # Pivot sums
        pivot_units = grouped.pivot(
            index="destination_warehouse_id",
            columns="container_type",
            values="sum_units"
        ).fillna(0)

        pivot_counts = grouped.pivot(
            index="destination_warehouse_id",
            columns="container_type",
            values="container_count"
        ).fillna(0)

        logger.debug(f"[ICQA PROCESS] pivot_units shape = {pivot_units.shape}")
        logger.debug(f"[ICQA PROCESS] pivot_counts shape = {pivot_counts.shape}")

        # Build aggregator rows
        for wh in pivot_units.index:
            row_dict = {}
            row_dict["destination_warehouse"] = wh

            # total_units = sum of all container types
            total_units = pivot_units.loc[wh].sum()
            row_dict["units"] = float(total_units)

            # container counts by known container_type
            cases_count = pivot_counts.loc[wh].get("CASE", 0.0)
            totes_count = pivot_counts.loc[wh].get("TOTE", 0.0)
            pax_count   = pivot_counts.loc[wh].get("PAX",  0.0)
            row_dict["cases"] = float(cases_count)
            row_dict["Totes"] = float(totes_count)
            row_dict["PAX"]   = float(pax_count)

            # total containers
            row_dict["containers"] = float(pivot_counts.loc[wh].sum())

            # units in each container type
            units_in_cases = pivot_units.loc[wh].get("CASE", 0.0)
            units_in_totes = pivot_units.loc[wh].get("TOTE", 0.0)
            units_in_pax   = pivot_units.loc[wh].get("PAX",  0.0)
            row_dict["Units_in_Cases"] = float(units_in_cases)
            row_dict["Units_in_Totes"] = float(units_in_totes)
            row_dict["Units_in_Pax"]   = float(units_in_pax)

            # metrics: UPC, UPT, UPP
            row_dict["UPC"] = float(units_in_cases / cases_count if cases_count else 0.0)
            row_dict["UPT"] = float(units_in_totes / totes_count if totes_count else 0.0)
            row_dict["UPP"] = float(units_in_pax   / pax_count   if pax_count   else 0.0)

            icqa_aggregated.append(row_dict)

        logger.info(f"[ICQA PROCESS] Aggregated data built. Row count = {len(icqa_aggregated)}")

    except Exception as e:
        logger.error(f"[ICQA PROCESS] Error building aggregated data: {e}", exc_info=True)

    # --- PART C: Summary
    icqa_summary = {}
    try:
        agg_df = pd.DataFrame(icqa_aggregated) if icqa_aggregated else pd.DataFrame()
        if not agg_df.empty:
            total_units = agg_df["units"].sum()
            total_cases = agg_df["cases"].sum()
            total_totes = agg_df["Totes"].sum()
            total_pax   = agg_df["PAX"].sum()

            total_units_in_cases = agg_df["Units_in_Cases"].sum()
            total_units_in_totes = agg_df["Units_in_Totes"].sum()
            total_units_in_pax   = agg_df["Units_in_Pax"].sum()

            global_upc = (total_units_in_cases / total_cases) if total_cases else 0.0
            global_upt = (total_units_in_totes / total_totes) if total_totes else 0.0
            global_upp = (total_units_in_pax   / total_pax)   if total_pax   else 0.0

            average_upc = agg_df["UPC"].mean() if "UPC" in agg_df.columns else 0.0
            average_upt = agg_df["UPT"].mean() if "UPT" in agg_df.columns else 0.0
            average_upp = agg_df["UPP"].mean() if "UPP" in agg_df.columns else 0.0

            icqa_summary = {
                "Units":          float(total_units),
                "Cases":          float(total_cases),
                "Totes":          float(total_totes),
                "Pax":            float(total_pax),
                "Units in Cases": float(total_units_in_cases),
                "Units in Totes": float(total_units_in_totes),
                "Units in Pax":   float(total_units_in_pax),
                "UPC": float(global_upc),
                "UPT": float(global_upt),
                "UPP": float(global_upp),
                "Average UPC": float(average_upc),
                "Average UPT": float(average_upt),
                "Average Pax": float(average_upp),
            }
        logger.info("[ICQA PROCESS] Summary generated successfully.")
    except Exception as e:
        logger.error(f"[ICQA PROCESS] Error building summary: {e}", exc_info=True)

    # --- Remove the CSV if you no longer need it
    try:
        os.remove(csv_path)
        logger.info(f"[ICQA PROCESS] Removed temp file: {csv_path}")
    except Exception as e:
        logger.error(f"[ICQA PROCESS] Error removing temp file: {e}", exc_info=True)

    # --- Replace NaN with "NaN" for JSON serialization
    icqa_unaggregated  = _fix_nan_in_list_of_dicts(icqa_unaggregated)
    icqa_aggregated    = _fix_nan_in_list_of_dicts(icqa_aggregated)
    icqa_summary       = _fix_nan_in_summary(icqa_summary)

    # Return final data
    return icqa_unaggregated, icqa_aggregated, icqa_summary
