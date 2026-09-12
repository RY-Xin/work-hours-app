import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date, time, timedelta


# =========================================================
# Pay Period Settings
# =========================================================

# Your company's pay period:
# Aug 24 - Sep 6, 2026
PAY_PERIOD_START = date(2026, 8, 24)

PAY_PERIOD_LENGTH = 14


# =========================================================
# Supabase Connection
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# Supabase Helpers
# =========================================================

def normalize_time(value):
    """
    Supabase may return time as HH:MM:SS.
    The app only needs HH:MM.
    """
    if value is None:
        return ""

    return str(value)[:5]


def normalize_record(row):
    """
    Convert a Supabase row into the same tuple structure
    used by the original SQLite version.
    """

    return (
        row["id"],
        str(row["work_date"]),
        normalize_time(row["start_time"]),
        normalize_time(row["end_time"]),
        row.get("break_minutes") or 0,
        float(row["total_hours"]),
        row.get("notes") or "",
    )


# =========================================================
# Database Operations
# =========================================================

def add_work_session(
    work_date,
    start_time,
    end_time,
    break_minutes,
    total_hours,
    notes
):

    response = (
        supabase
        .table("work_sessions")
        .insert({
            "work_date": work_date,
            "start_time": start_time,
            "end_time": end_time,
            "break_minutes": break_minutes,
            "total_hours": total_hours,
            "notes": notes or None,
        })
        .execute()
    )

    return response


def get_work_history():

    response = (
        supabase
        .table("work_sessions")
        .select("*")
        .order("work_date", desc=True)
        .order("start_time", desc=True)
        .execute()
    )

    rows = response.data or []

    return [
        normalize_record(row)
        for row in rows
    ]


def get_period_records(
    period_start,
    period_end
):

    response = (
        supabase
        .table("work_sessions")
        .select("*")
        .gte(
            "work_date",
            period_start.isoformat()
        )
        .lte(
            "work_date",
            period_end.isoformat()
        )
        .order("work_date")
        .order("start_time")
        .execute()
    )

    rows = response.data or []

    return [
        normalize_record(row)
        for row in rows
    ]


def update_work_session(
    record_id,
    work_date,
    start_time,
    end_time,
    break_minutes,
    total_hours,
    notes
):

    response = (
        supabase
        .table("work_sessions")
        .update({
            "work_date": work_date,
            "start_time": start_time,
            "end_time": end_time,
            "break_minutes": break_minutes,
            "total_hours": total_hours,
            "notes": notes or None,
        })
        .eq("id", record_id)
        .execute()
    )

    return response


def delete_work_session(record_id):

    response = (
        supabase
        .table("work_sessions")
        .delete()
        .eq("id", record_id)
        .execute()
    )

    return response


# =========================================================
# Calculate Hours
# =========================================================

def calculate_hours(
    start_time,
    end_time,
    break_minutes
):

    start_datetime = datetime.combine(
        date.today(),
        start_time
    )

    end_datetime = datetime.combine(
        date.today(),
        end_time
    )

    # Support overnight work
    if end_datetime < start_datetime:
        end_datetime += timedelta(days=1)

    total_seconds = (
        end_datetime - start_datetime
    ).total_seconds()

    total_hours = total_seconds / 3600

    total_hours -= break_minutes / 60

    return max(total_hours, 0)


# =========================================================
# Pay Period Calculation
# =========================================================

def get_pay_period(target_date):

    days_since_start = (
        target_date - PAY_PERIOD_START
    ).days

    period_number = (
        days_since_start // PAY_PERIOD_LENGTH
    )

    period_start = (
        PAY_PERIOD_START
        + timedelta(
            days=period_number * PAY_PERIOD_LENGTH
        )
    )

    period_end = (
        period_start
        + timedelta(days=PAY_PERIOD_LENGTH - 1)
    )

    return period_start, period_end


def format_period(
    period_start,
    period_end
):

    return (
        f"{period_start.strftime('%b %d')} "
        f"– "
        f"{period_end.strftime('%b %d, %Y')}"
    )


# =========================================================
# App
# =========================================================

st.title("⏱ Work Hours Tracker")


# =========================================================
# Pay Period Navigation
# =========================================================

today = date.today()


# Initialize selected pay period
if "period_offset" not in st.session_state:

    st.session_state.period_offset = 0


# Get current pay period
current_start, current_end = get_pay_period(
    today
)


# Apply navigation offset
selected_start = (
    current_start
    + timedelta(
        days=(
            st.session_state.period_offset
            * PAY_PERIOD_LENGTH
        )
    )
)

selected_end = (
    selected_start
    + timedelta(
        days=PAY_PERIOD_LENGTH - 1
    )
)


st.subheader("Pay Period")


# =========================================================
# Navigation Buttons
# =========================================================

left_col, middle_col, right_col = st.columns(
    [1, 2, 1]
)


with left_col:

    if st.button("← Previous"):

        st.session_state.period_offset -= 1

        st.rerun()


with middle_col:

    st.markdown(
        f"""
        <h3 style='text-align: center;'>
            {format_period(
                selected_start,
                selected_end
            )}
        </h3>
        """,
        unsafe_allow_html=True
    )


with right_col:

    if st.button("Next →"):

        st.session_state.period_offset += 1

        st.rerun()


# =========================================================
# Return to Current Period
# =========================================================

if st.session_state.period_offset != 0:

    if st.button("Today / Current Period"):

        st.session_state.period_offset = 0

        st.rerun()


# =========================================================
# Pay Period Summary
# =========================================================

try:

    period_records = get_period_records(
        selected_start,
        selected_end
    )

except Exception:

    st.error(
        "Unable to load work records from Supabase. "
        "Please check your Supabase connection and Secrets."
    )

    period_records = []


total_period_hours = sum(
    record[5]
    for record in period_records
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Total Hours",
        f"{total_period_hours:.2f} h"
    )


with col2:

    st.metric(
        "Days Worked",
        len(period_records)
    )


# =========================================================
# Daily Hours
# =========================================================

st.markdown("### Daily Hours")


if period_records:

    for record in period_records:

        work_date_str = record[1]
        start_time_str = record[2]
        end_time_str = record[3]
        break_minutes_value = record[4]
        total_hours_value = record[5]
        notes_value = record[6]


        col1, col2, col3 = st.columns(
            [1.5, 2, 1]
        )


        col1.write(
            f"**{work_date_str}**"
        )


        col2.write(
            f"{start_time_str} → {end_time_str}"
        )


        col3.write(
            f"**{total_hours_value:.2f} h**"
        )


        if break_minutes_value > 0:

            st.caption(
                f"Break: {break_minutes_value} min"
            )


        if notes_value:

            st.caption(
                f"Notes: {notes_value}"
            )

else:

    st.info(
        "No work records in this pay period."
    )


# =========================================================
# Add Work Record
# =========================================================

st.divider()

st.subheader("Add Work Record")


work_date = st.date_input(
    "Date",
    value=today
)


start_time = st.time_input(
    "Start Time",
    value=time(5, 30)
)


end_time = st.time_input(
    "End Time",
    value=time(14, 0)
)


break_minutes = st.number_input(
    "Break (minutes)",
    min_value=0,
    value=0,
    step=15
)


notes = st.text_input(
    "Notes",
    placeholder="Optional"
)


# =========================================================
# Preview Total Hours
# =========================================================

total_hours = calculate_hours(
    start_time,
    end_time,
    break_minutes
)


st.metric(
    "Total Hours",
    f"{total_hours:.2f} hours"
)


# =========================================================
# Add Record
# =========================================================

if st.button(
    "Add Record",
    type="primary"
):

    try:

        add_work_session(
            work_date.isoformat(),
            start_time.strftime("%H:%M"),
            end_time.strftime("%H:%M"),
            break_minutes,
            total_hours,
            notes
        )

        st.success(
            "Work record added!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Unable to add the work record: {e}"
        )


# =========================================================
# Full Work History
# =========================================================

st.divider()

st.subheader("Work History")


try:

    records = get_work_history()

except Exception:

    st.error(
        "Unable to load work history from Supabase."
    )

    records = []


if records:

    for record in records:

        record_id = record[0]
        work_date_str = record[1]
        start_time_str = record[2]
        end_time_str = record[3]
        break_minutes_value = record[4]
        total_hours_value = record[5]
        notes_value = record[6]


        with st.container():

            col1, col2, col3, col4, col5 = st.columns(
                [1.5, 2, 1, 0.6, 0.6]
            )


            col1.write(
                f"**{work_date_str}**"
            )


            col2.write(
                f"{start_time_str} → {end_time_str}"
            )


            col3.write(
                f"**{total_hours_value:.2f} h**"
            )


            # =================================================
            # Edit
            # =================================================

            if col4.button(
                "✏️",
                key=f"edit_{record_id}"
            ):

                st.session_state.editing_id = record_id

                st.rerun()


            # =================================================
            # Delete
            # =================================================

            if col5.button(
                "🗑️",
                key=f"delete_{record_id}"
            ):

                st.session_state.deleting_id = record_id

                st.rerun()


            if break_minutes_value > 0:

                st.caption(
                    f"Break: {break_minutes_value} min"
                )


            if notes_value:

                st.caption(
                    f"Notes: {notes_value}"
                )


            # =================================================
            # Edit Form
            # =================================================

            if st.session_state.get(
                "editing_id"
            ) == record_id:

                st.markdown(
                    "#### Edit Record"
                )


                edit_date = st.date_input(
                    "Date",
                    value=datetime.strptime(
                        work_date_str,
                        "%Y-%m-%d"
                    ).date(),
                    key=f"edit_date_{record_id}"
                )


                edit_start = st.time_input(
                    "Start Time",
                    value=datetime.strptime(
                        start_time_str,
                        "%H:%M"
                    ).time(),
                    key=f"edit_start_{record_id}"
                )


                edit_end = st.time_input(
                    "End Time",
                    value=datetime.strptime(
                        end_time_str,
                        "%H:%M"
                    ).time(),
                    key=f"edit_end_{record_id}"
                )


                edit_break = st.number_input(
                    "Break (minutes)",
                    min_value=0,
                    value=break_minutes_value,
                    step=15,
                    key=f"edit_break_{record_id}"
                )


                edit_notes = st.text_input(
                    "Notes",
                    value=notes_value or "",
                    key=f"edit_notes_{record_id}"
                )


                edit_total = calculate_hours(
                    edit_start,
                    edit_end,
                    edit_break
                )


                st.metric(
                    "New Total Hours",
                    f"{edit_total:.2f} hours"
                )


                save_col, cancel_col = st.columns(2)


                # =================================================
                # Save Changes
                # =================================================

                if save_col.button(
                    "Save Changes",
                    key=f"save_{record_id}",
                    type="primary"
                ):

                    try:

                        update_work_session(
                            record_id,
                            edit_date.isoformat(),
                            edit_start.strftime("%H:%M"),
                            edit_end.strftime("%H:%M"),
                            edit_break,
                            edit_total,
                            edit_notes
                        )

                        st.session_state.editing_id = None

                        st.success(
                            "Changes saved!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to save changes: {e}"
                        )


                # =================================================
                # Cancel Edit
                # =================================================

                if cancel_col.button(
                    "Cancel",
                    key=f"cancel_{record_id}"
                ):

                    st.session_state.editing_id = None

                    st.rerun()


            # =================================================
            # Delete Confirmation
            # =================================================

            if st.session_state.get(
                "deleting_id"
            ) == record_id:

                st.warning(
                    "Are you sure you want to delete this record?"
                )


                delete_col, cancel_col = st.columns(2)


                # =================================================
                # Confirm Delete
                # =================================================

                if delete_col.button(
                    "Yes, Delete",
                    key=f"confirm_delete_{record_id}"
                ):

                    try:

                        delete_work_session(
                            record_id
                        )

                        st.session_state.deleting_id = None

                        st.success(
                            "Record deleted!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to delete the record: {e}"
                        )


                # =================================================
                # Cancel Delete
                # =================================================

                if cancel_col.button(
                    "Cancel",
                    key=f"cancel_delete_{record_id}"
                ):

                    st.session_state.deleting_id = None

                    st.rerun()


            st.divider()


else:

    st.info(
        "No work records yet."
    )
