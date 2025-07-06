import logging
from datetime import datetime
from utils.utils import get_value_or_default  # or your local helper

logger = logging.getLogger(__name__)

def process_dock_master_data(data, start_datetime=None, end_datetime=None):
    """
    Processes DockMaster data, returning both unfiltered and filtered results.
    Datetimes are converted to strings so we don't break JSON serialization.
    """

    start_dt = None
    end_dt = None

    # 1) Convert string-based start/end times (ISO) to datetime objects if needed
    if isinstance(start_datetime, str):
        try:
            start_dt = datetime.fromisoformat(start_datetime)
            logger.debug(f"[DEBUG] Converted start_datetime '{start_datetime}' to datetime: {start_dt}")
        except ValueError:
            logger.warning(f"[DEBUG] Could not parse start_datetime: {start_datetime}")
            start_dt = None
    elif isinstance(start_datetime, datetime):
        start_dt = start_datetime

    if isinstance(end_datetime, str):
        try:
            end_dt = datetime.fromisoformat(end_datetime)
            logger.debug(f"[DEBUG] Converted end_datetime '{end_datetime}' to datetime: {end_dt}")
        except ValueError:
            logger.warning(f"[DEBUG] Could not parse end_datetime: {end_datetime}")
            end_dt = None
    elif isinstance(end_datetime, datetime):
        end_dt = end_datetime

    # 2) Unfiltered array of processed appointments
    unfiltered_data = []
    appointment_list = data.get("AppointmentList", [])

    logger.debug(f"[DEBUG] Found {len(appointment_list)} appointments in raw data.")

    for appointment in appointment_list:
        attrs = appointment.get("attributes", {})

        raw_time_str = (
            appointment
            .get("appointmentScheduleDates", {})
            .get("localStartDate", {})
            .get("timeDateWithTimezone", "")
        )
        parsed_time_str = raw_time_str.replace(" GMT", "")

        try:
            appointment_dt = datetime.strptime(parsed_time_str, "%Y/%m/%d %H:%M:%S")
            iso_dt_str = appointment_dt.isoformat()
        except ValueError:
            ## logger.warning(f"Could not parse date/time: {raw_time_str}")
            appointment_dt = None
            iso_dt_str = None

        processed_appointment = {
            "AppointmentScheduleDate": raw_time_str,
            "AppointmentDateTimeObj": iso_dt_str,
            "Carrier_Load_Type": get_value_or_default(attrs, "CARRIER_LOAD_TYPE", "none"),
            "ISA": appointment.get("inboundShipmentAppointmentId", ""),
            "ISA_TYPE": appointment.get("appointmentType", ""),
            "Unit_Count": appointment.get("unitCount", 0),
            "Carton_Count": appointment.get("cartonCount", 0),
            "Pallet_Count": appointment.get("palletCount", 0),
            "Door_Number": appointment.get("doorNumber", ""),
            "SCAC": appointment.get("standardCarrierAlphaCode", ""),
            "Status": appointment.get("status", "")
        }
        unfiltered_data.append(processed_appointment)

    # 3) Filter if we have valid start_dt/end_dt
    if start_dt and end_dt:
        filtered_data = []
        for idx, appt in enumerate(unfiltered_data):
            raw_time_str = (
                appointment_list[idx]
                .get("appointmentScheduleDates", {})
                .get("localStartDate", {})
                .get("timeDateWithTimezone", "")
            )
            parsed_time_str = raw_time_str.replace(" GMT", "")

            try:
                real_dt = datetime.strptime(parsed_time_str, "%Y/%m/%d %H:%M:%S")
            except ValueError:
                real_dt = None

            if real_dt and (start_dt <= real_dt <= end_dt):
                filtered_data.append(appt)
    else:
        filtered_data = unfiltered_data

    logger.info(f"Processed {len(unfiltered_data)} total DockMaster appointments.")
    logger.info(f"Filtered DockMaster appointments: {len(filtered_data)} within shift range.")

    return {
        "DockMaster": unfiltered_data,
        "DockMasterFiltered": filtered_data
    }
