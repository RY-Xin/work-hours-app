import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date, time, timedelta


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Work Hours Tracker",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Pay Period Settings
# =========================================================

PAY_PERIOD_START = date(2026, 8, 24)
PAY_PERIOD_LENGTH = 14


# =========================================================
# Custom CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       Global
       ===================================================== */

    .block-container {
        max-width: 720px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }


    /* =====================================================
       Main Title
       ===================================================== */

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.25rem;
    }


    /* =====================================================
       Pay Period
       ===================================================== */

    .period-card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }

    .period-label {
        text-align: center;
        color: #6b7280;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.15rem;
    }

    .period-title {
        text-align: center;
        font-size: 1.15rem;
        font-weight: 650;
    }


    /* =====================================================
       Summary
       ===================================================== */

    .summary-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.15rem;
        background: white;
        margin-bottom: 1.5rem;
    }

    .summary-label {
        color: #6b7280;
        font-size: 0.82rem;
        margin-bottom: 0.15rem;
    }

    .summary-value {
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.15;
    }

    .summary-secondary {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }


    /* =====================================================
       Section Titles
       ===================================================== */

    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
    }


    /* =====================================================
       Daily Record Card
       ===================================================== */

    .record-card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        background: white;
    }

    .record-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.45rem;
    }

    .record-date {
        font-size: 1rem;
        font-weight: 650;
    }

    .record-hours {
        font-size: 1rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .record-time {
        font-size: 0.95rem;
        color: #374151;
    }

    .record-detail {
        color: #6b7280;
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }


    /* =====================================================
       Add Record Area
       ===================================================== */

    .add-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.1rem;
        background: white;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }


    /* =====================================================
       Mobile
       ===================================================== */

    @media (max-width: 600px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .app-title {
            font-size: 1.7rem;
        }

        .summary-value {
            font-size: 1.65rem;
        }

        .record-card {
            padding: 0.9rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


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

    if value is None:
        return ""

    return str(value)[:5]


def normalize_record(row):

    return (
        row["id"],
        str(row["work_date"]),
        normalize_time(row["start_time"]),
        normalize_time(row["end_time"]),
        row.get("break_minutes") or 0,
        float(row["total_hours"]),
        row.get("notes") or "",
    )


def add_work_session(
    work_date,
    start_time,
    end_time,
    break_minutes,
    total_hours,
    notes
):

    return (
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

    return (
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


def delete_work_session(record_id):

    return (
        supabase
        .table("work_sessions")
        .delete()
        .eq("id", record_id)
        .execute()
    )


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

    if end_datetime < start_datetime:
        end_datetime += timedelta(days=1)

    total_seconds = (
        end_datetime - start_datetime
    ).total_seconds()

    total_hours = total_seconds / 3600

    total_hours -= break_minutes / 60

    return max(total_hours, 0)


# =========================================================
# Pay Period
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
        + timedelta(
            days=PAY_PERIOD_LENGTH - 1
        )
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


def format_display_date(date_string):

    value = datetime.strptime(
        date_string,
        "%Y-%m-%d"
    ).date()

    return value.strftime("%a, %b %d")


def format_display_time(time_string):

    value = datetime.strptime(
        time_string,
        "%H:%M"
    ).time()

    return value.strftime("%-I:%M %p")


# =========================================================
# Session State
# =========================================================

if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

if "deleting_id" not in st.session_state:
    st.session_state.deleting_id = None

if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False


# =========================================================
# Current Date / Period
# =========================================================

today = date.today()

current_start, current_end = get_pay_period(today)

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


# =========================================================
# Header
# =========================================================

st.markdown(
    """
    <div class="app-title">⏱️ Work Hours</div>
    <div class="app-subtitle">
        Simple work time tracking
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Pay Period Navigation
# =========================================================

left_col, center_col, right_col = st.columns(
    [1, 4, 1]
)


with left_col:

    if st.button(
        "‹",
        key="previous_period",
        use_container_width=True
    ):

        st.session_state.period_offset -= 1

        st.rerun()


with center_col:

    st.markdown(
        f"""
        <div class="period-card">
            <div class="period-label">
                Pay Period
            </div>
            <div class="period-title">
                {format_period(
                    selected_start,
                    selected_end
                )}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with right_col:

    if st.button(
        "›",
        key="next_period",
        use_container_width=True
    ):

        st.session_state.period_offset += 1

        st.rerun()


if st.session_state.period_offset != 0:

    if st.button(
        "Current Period",
        use_container_width=True
    ):

        st.session_state.period_offset = 0

        st.rerun()


# =========================================================
# Load Current Period
# =========================================================

try:

    period_records = get_period_records(
        selected_start,
        selected_end
    )

except Exception as e:

    st.error(
        "Unable to load work records from Supabase."
    )

    period_records = []


# =========================================================
# Summary
# =========================================================

total_period_hours = sum(
    record[5]
    for record in period_records
)


st.markdown(
    f"""
    <div class="summary-card">

        <div class="summary-label">
            Total Hours
        </div>

        <div class="summary-value">
            {total_period_hours:.2f} h
        </div>

        <div class="summary-secondary">
            {len(period_records)}
            {"day" if len(period_records) == 1 else "days"}
            worked
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Daily Hours
# =========================================================

st.markdown(
    '<div class="section-title">Daily Hours</div>',
    unsafe_allow_html=True
)


if period_records:

    for record in period_records:

        record_id = record[0]
        work_date_str = record[1]
        start_time_str = record[2]
        end_time_str = record[3]
        break_minutes_value = record[4]
        total_hours_value = record[5]
        notes_value = record[6]

        display_date = format_display_date(
            work_date_str
        )

        display_start = format_display_time(
            start_time_str
        )

        display_end = format_display_time(
            end_time_str
        )


        # =================================================
        # Record Card
        # =================================================

        st.markdown(
            f"""
            <div class="record-card">

                <div class="record-header">

                    <div class="record-date">
                        {display_date}
                    </div>

                    <div class="record-hours">
                        {total_hours_value:.2f} h
                    </div>

                </div>

                <div class="record-time">
                    {display_start} → {display_end}
                </div>

                <div class="record-detail">
                    Break: {break_minutes_value} min
                </div>

                {
                    f'<div class="record-detail">Notes: {notes_value}</div>'
                    if notes_value
                    else ''
                }

            </div>
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # Edit / Delete
        # =================================================

        edit_col, delete_col = st.columns(2)


        if edit_col.button(
            "✏️ Edit",
            key=f"period_edit_{record_id}",
            use_container_width=True
        ):

            st.session_state.editing_id = record_id
            st.session_state.deleting_id = None

            st.rerun()


        if delete_col.button(
            "🗑️ Delete",
            key=f"period_delete_{record_id}",
            use_container_width=True
        ):

            st.session_state.deleting_id = record_id
            st.session_state.editing_id = None

            st.rerun()


        # =================================================
        # Edit Form
        # =================================================

        if st.session_state.editing_id == record_id:

            st.markdown("#### Edit Record")


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
                "Total Hours",
                f"{edit_total:.2f} h"
            )


            save_col, cancel_col = st.columns(2)


            if save_col.button(
                "Save Changes",
                key=f"save_{record_id}",
                type="primary",
                use_container_width=True
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

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Unable to save changes: {e}"
                    )


            if cancel_col.button(
                "Cancel",
                key=f"cancel_{record_id}",
                use_container_width=True
            ):

                st.session_state.editing_id = None

                st.rerun()


        # =================================================
        # Delete Confirmation
        # =================================================

        if st.session_state.deleting_id == record_id:

            st.warning(
                "Delete this work record?"
            )


            delete_col, cancel_col = st.columns(2)


            if delete_col.button(
                "Yes, Delete",
                key=f"confirm_delete_{record_id}",
                type="primary",
                use_container_width=True
            ):

                try:

                    delete_work_session(
                        record_id
                    )

                    st.session_state.deleting_id = None

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Unable to delete the record: {e}"
                    )


            if cancel_col.button(
                "Cancel",
                key=f"cancel_delete_{record_id}",
                use_container_width=True
            ):

                st.session_state.deleting_id = None

                st.rerun()


else:

    st.info(
        "No work records in this pay period."
    )


# =========================================================
# Add Work Record
# =========================================================

st.markdown(
    '<div class="section-title">Add Work Record</div>',
    unsafe_allow_html=True
)


if not st.session_state.show_add_form:

    if st.button(
        "＋ Add Work Record",
        type="primary",
        use_container_width=True
    ):

        st.session_state.show_add_form = True

        st.rerun()


else:

    with st.container(border=True):

        st.markdown("### New Work Record")


        add_date = st.date_input(
            "Date",
            value=today,
            key="add_date"
        )


        time_col1, time_col2 = st.columns(2)


        with time_col1:

            add_start = st.time_input(
                "Start Time",
                value=time(5, 30),
                key="add_start"
            )


        with time_col2:

            add_end = st.time_input(
                "End Time",
                value=time(14, 0),
                key="add_end"
            )


        add_break = st.number_input(
            "Break (minutes)",
            min_value=0,
            value=0,
            step=15,
            key="add_break"
        )


        add_notes = st.text_input(
            "Notes",
            placeholder="Optional",
            key="add_notes"
        )


        add_total = calculate_hours(
            add_start,
            add_end,
            add_break
        )


        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">
                    Total Hours
                </div>
                <div class="summary-value">
                    {add_total:.2f} h
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        save_col, cancel_col = st.columns(2)


        if save_col.button(
            "Add Record",
            type="primary",
            use_container_width=True,
            key="add_record"
        ):

            try:

                add_work_session(
                    add_date.isoformat(),
                    add_start.strftime("%H:%M"),
                    add_end.strftime("%H:%M"),
                    add_break,
                    add_total,
                    add_notes
                )

                st.session_state.show_add_form = False

                st.success(
                    "Work record added!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to add the work record: {e}"
                )


        if cancel_col.button(
            "Cancel",
            use_container_width=True,
            key="cancel_add"
        ):

            st.session_state.show_add_form = False

            st.rerun()


# =========================================================
# Work History
# =========================================================

st.markdown(
    '<div class="section-title">Work History</div>',
    unsafe_allow_html=True
)


try:

    records = get_work_history()

except Exception:

    records = []


# Show history outside selected pay period
history_records = [
    record
    for record in records
    if not (
        selected_start.isoformat()
        <= record[1]
        <= selected_end.isoformat()
    )
]


if history_records:

    with st.expander(
        f"View Previous Records ({len(history_records)})"
    ):

        for record in history_records:

            record_id = record[0]
            work_date_str = record[1]
            start_time_str = record[2]
            end_time_str = record[3]
            break_minutes_value = record[4]
            total_hours_value = record[5]
            notes_value = record[6]


            display_date = format_display_date(
                work_date_str
            )

            display_start = format_display_time(
                start_time_str
            )

            display_end = format_display_time(
                end_time_str
            )


            st.markdown(
                f"""
                <div class="record-card">

                    <div class="record-header">

                        <div class="record-date">
                            {display_date}
                        </div>

                        <div class="record-hours">
                            {total_hours_value:.2f} h
                        </div>

                    </div>

                    <div class="record-time">
                        {display_start} → {display_end}
                    </div>

                    <div class="record-detail">
                        Break: {break_minutes_value} min
                    </div>

                    {
                        f'<div class="record-detail">Notes: {notes_value}</div>'
                        if notes_value
                        else ''
                    }

                </div>
                """,
                unsafe_allow_html=True
            )

            edit_col, delete_col = st.columns(2)


            if edit_col.button(
                "✏️ Edit",
                key=f"history_edit_{record_id}",
                use_container_width=True
            ):

                st.session_state.editing_id = record_id
                st.session_state.deleting_id = None

                st.rerun()


            if delete_col.button(
                "🗑️ Delete",
                key=f"history_delete_{record_id}",
                use_container_width=True
            ):

                st.session_state.deleting_id = record_id
                st.session_state.editing_id = None

                st.rerun()


else:

    st.caption(
        "No previous records."
    )
```
