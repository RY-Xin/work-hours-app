import streamlit as st
import datetime
from supabase import create_client, Client


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Work Hours",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Custom CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- General ---------- */

    .stApp {
        background: #f7f8fa;
    }

    .block-container {
        max-width: 680px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.3px;
    }

    /* ---------- Hide Streamlit extras ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* ---------- App Header ---------- */

    .app-title {
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 2px;
        color: #111827;
    }

    .app-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 22px;
    }

    /* ---------- Pay Period ---------- */

    .period-label {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 4px;
        font-weight: 500;
    }

    .period-title {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 14px;
    }

    /* ---------- Summary Card ---------- */

    .summary-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 20px;
        margin-top: 8px;
        margin-bottom: 28px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    .summary-label {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 3px;
    }

    .summary-value {
        font-size: 34px;
        line-height: 1.1;
        font-weight: 750;
        color: #111827;
    }

    .summary-secondary {
        margin-top: 7px;
        font-size: 14px;
        color: #6b7280;
    }

    /* ---------- Section Title ---------- */

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-top: 4px;
        margin-bottom: 12px;
    }

    /* ---------- Record Card ---------- */

    .record-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.025);
    }

    .record-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }

    .record-date {
        font-size: 16px;
        font-weight: 650;
        color: #111827;
    }

    .record-hours {
        font-size: 17px;
        font-weight: 700;
        color: #111827;
        white-space: nowrap;
    }

    .record-time {
        margin-top: 8px;
        font-size: 15px;
        color: #374151;
    }

    .record-detail {
        margin-top: 5px;
        font-size: 13px;
        color: #6b7280;
    }

    /* ---------- Add Record ---------- */

    .add-title {
        font-size: 19px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    /* ---------- Mobile ---------- */

    @media (max-width: 600px) {

        .block-container {
            padding-left: 14px;
            padding-right: 14px;
            padding-top: 1.2rem;
        }

        .app-title {
            font-size: 27px;
        }

        .period-title {
            font-size: 20px;
        }

        .summary-card {
            border-radius: 16px;
            padding: 18px;
        }

        .summary-value {
            font-size: 32px;
        }

        .record-card {
            padding: 15px 16px;
            border-radius: 15px;
        }

        .record-date {
            font-size: 15px;
        }

        .record-hours {
            font-size: 16px;
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
# Constants
# =========================================================

PAY_PERIOD_START = datetime.date(2026, 8, 24)
PAY_PERIOD_LENGTH = 14


# =========================================================
# Helper Functions
# =========================================================

def normalize_time(value):
    """Convert Supabase time string to HH:MM."""
    if value is None:
        return None

    value = str(value)

    if len(value) >= 5:
        return value[:5]

    return value


def calculate_hours(start_time, end_time, break_minutes):
    """Calculate total worked hours."""

    start = datetime.datetime.combine(
        datetime.date.today(),
        start_time
    )

    end = datetime.datetime.combine(
        datetime.date.today(),
        end_time
    )

    if end <= start:
        end += datetime.timedelta(days=1)

    total_minutes = (end - start).total_seconds() / 60
    total_minutes -= break_minutes

    return max(total_minutes / 60, 0)


def format_date(date_value):
    """Format date like Mon, Sep 07."""

    if isinstance(date_value, str):
        date_value = datetime.date.fromisoformat(date_value)

    return date_value.strftime("%a, %b %d")


def format_time(time_value):
    """Format time like 5:20 AM."""

    if isinstance(time_value, str):
        time_value = datetime.time.fromisoformat(time_value)

    return time_value.strftime("%I:%M %p").lstrip("0")


def get_pay_period(offset=0):
    """
    Get pay period based on 14-day periods.

    offset = 0  -> current period
    offset = -1 -> previous period
    offset = 1  -> next period
    """

    today = datetime.date.today()

    days_since_start = (today - PAY_PERIOD_START).days

    current_period_index = days_since_start // PAY_PERIOD_LENGTH

    period_index = current_period_index + offset

    start_date = PAY_PERIOD_START + datetime.timedelta(
        days=period_index * PAY_PERIOD_LENGTH
    )

    end_date = start_date + datetime.timedelta(
        days=PAY_PERIOD_LENGTH - 1
    )

    return start_date, end_date


# =========================================================
# Supabase CRUD
# =========================================================

def add_work_session(
    work_date,
    start_time,
    end_time,
    break_minutes,
    notes
):
    total_hours = calculate_hours(
        start_time,
        end_time,
        break_minutes
    )

    data = {
        "work_date": work_date.isoformat(),
        "start_time": start_time.strftime("%H:%M:%S"),
        "end_time": end_time.strftime("%H:%M:%S"),
        "break_minutes": break_minutes,
        "total_hours": total_hours,
        "notes": notes.strip() if notes else None,
    }

    supabase.table("work_sessions").insert(data).execute()


def get_work_history():
    response = (
        supabase
        .table("work_sessions")
        .select("*")
        .order("work_date", desc=True)
        .order("start_time", desc=True)
        .execute()
    )

    return response.data or []


def get_period_records(start_date, end_date):
    response = (
        supabase
        .table("work_sessions")
        .select("*")
        .gte("work_date", start_date.isoformat())
        .lte("work_date", end_date.isoformat())
        .order("work_date", desc=False)
        .order("start_time", desc=False)
        .execute()
    )

    return response.data or []


def update_work_session(
    record_id,
    work_date,
    start_time,
    end_time,
    break_minutes,
    notes
):
    total_hours = calculate_hours(
        start_time,
        end_time,
        break_minutes
    )

    data = {
        "work_date": work_date.isoformat(),
        "start_time": start_time.strftime("%H:%M:%S"),
        "end_time": end_time.strftime("%H:%M:%S"),
        "break_minutes": break_minutes,
        "total_hours": total_hours,
        "notes": notes.strip() if notes else None,
    }

    (
        supabase
        .table("work_sessions")
        .update(data)
        .eq("id", record_id)
        .execute()
    )


def delete_work_session(record_id):
    (
        supabase
        .table("work_sessions")
        .delete()
        .eq("id", record_id)
        .execute()
    )


# =========================================================
# App Header
# =========================================================

st.markdown(
    """
    <div class="app-title">⏱️ Work Hours</div>
    <div class="app-subtitle">Simple work time tracking</div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Pay Period Navigation
# =========================================================

if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0


nav_col1, nav_col2, nav_col3 = st.columns(
    [1, 2, 1],
    vertical_alignment="center"
)


with nav_col1:
    if st.button("‹ Previous", use_container_width=True):
        st.session_state.period_offset -= 1
        st.rerun()


with nav_col2:
    start_date, end_date = get_pay_period(
        st.session_state.period_offset
    )

    st.markdown(
        f"""
        <div style="
            text-align:center;
            font-size:13px;
            color:#6b7280;
            padding-top:7px;
        ">
            Pay Period
        </div>

        <div style="
            text-align:center;
            font-size:17px;
            font-weight:700;
            color:#111827;
            padding-top:2px;
        ">
            {start_date.strftime("%b %d")}
            –
            {end_date.strftime("%b %d, %Y")}
        </div>
        """,
        unsafe_allow_html=True,
    )


with nav_col3:
    if st.button("Next ›", use_container_width=True):
        st.session_state.period_offset += 1
        st.rerun()


# =========================================================
# Current Period Records
# =========================================================

try:
    period_records = get_period_records(
        start_date,
        end_date
    )

except Exception as e:
    st.error("Unable to load work records from Supabase.")
    st.caption(str(e))
    st.stop()


total_hours = sum(
    float(record.get("total_hours", 0) or 0)
    for record in period_records
)

days_worked = len(period_records)


# =========================================================
# Summary Card
# =========================================================

st.markdown(
    f"""
    <div class="summary-card">

        <div class="summary-label">
            Total Hours
        </div>

        <div class="summary-value">
            {total_hours:.2f} h
        </div>

        <div class="summary-secondary">
            {days_worked} day{"s" if days_worked != 1 else ""} worked
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Daily Hours
# =========================================================

st.markdown(
    '<div class="section-title">Daily Hours</div>',
    unsafe_allow_html=True,
)


if not period_records:

    st.info("No work records for this pay period yet.")

else:

    for record in period_records:

        work_date = datetime.date.fromisoformat(
            record["work_date"]
        )

        start_time = datetime.time.fromisoformat(
            normalize_time(record["start_time"])
        )

        end_time = datetime.time.fromisoformat(
            normalize_time(record["end_time"])
        )

        hours = float(
            record.get("total_hours", 0) or 0
        )

        break_minutes = int(
            record.get("break_minutes", 0) or 0
        )

        notes = record.get("notes")

        st.markdown(
            f"""
            <div class="record-card">

                <div class="record-header">

                    <div class="record-date">
                        {format_date(work_date)}
                    </div>

                    <div class="record-hours">
                        {hours:.2f} h
                    </div>

                </div>

                <div class="record-time">
                    {format_time(start_time)}
                    →
                    {format_time(end_time)}
                </div>

                <div class="record-detail">
                    Break: {break_minutes} min
                </div>

                {
                    f'<div class="record-detail">Notes: {notes}</div>'
                    if notes
                    else ""
                }

            </div>
            """,
            unsafe_allow_html=True,
        )

        edit_col, delete_col = st.columns(2)

        with edit_col:

            edit_key = f"edit_{record['id']}"

            if st.button(
                "✏️ Edit",
                key=edit_key,
                use_container_width=True
            ):
                st.session_state.editing_id = record["id"]
                st.rerun()

        with delete_col:

            delete_key = f"delete_{record['id']}"

            if st.button(
                "🗑️ Delete",
                key=delete_key,
                use_container_width=True
            ):
                st.session_state.deleting_id = record["id"]
                st.rerun()


# =========================================================
# Edit Record
# =========================================================

if "editing_id" in st.session_state:

    editing_id = st.session_state.editing_id

    editing_record = next(
        (
            record
            for record in period_records
            if record["id"] == editing_id
        ),
        None
    )

    if editing_record:

        st.divider()

        st.markdown(
            '<div class="section-title">Edit Work Record</div>',
            unsafe_allow_html=True,
        )

        edit_date = datetime.date.fromisoformat(
            editing_record["work_date"]
        )

        edit_start = datetime.time.fromisoformat(
            normalize_time(
                editing_record["start_time"]
            )
        )

        edit_end = datetime.time.fromisoformat(
            normalize_time(
                editing_record["end_time"]
            )
        )

        edit_break = int(
            editing_record.get("break_minutes", 0) or 0
        )

        edit_notes = (
            editing_record.get("notes")
            or ""
        )

        with st.form(
            f"edit_form_{editing_id}"
        ):

            new_date = st.date_input(
                "Date",
                value=edit_date
            )

            new_start = st.time_input(
                "Start Time",
                value=edit_start
            )

            new_end = st.time_input(
                "End Time",
                value=edit_end
            )

            new_break = st.number_input(
                "Break (minutes)",
                min_value=0,
                max_value=300,
                value=edit_break,
                step=5
            )

            new_notes = st.text_input(
                "Notes",
                value=edit_notes
            )

            save_col, cancel_col = st.columns(2)

            with save_col:

                save_edit = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True
                )

            with cancel_col:

                cancel_edit = st.form_submit_button(
                    "Cancel",
                    use_container_width=True
                )

            if save_edit:

                try:

                    update_work_session(
                        editing_id,
                        new_date,
                        new_start,
                        new_end,
                        new_break,
                        new_notes
                    )

                    del st.session_state.editing_id

                    st.success(
                        "Work record updated."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Unable to update the record."
                    )

                    st.caption(str(e))

            if cancel_edit:

                del st.session_state.editing_id
                st.rerun()


# =========================================================
# Delete Confirmation
# =========================================================

if "deleting_id" in st.session_state:

    deleting_id = st.session_state.deleting_id

    deleting_record = next(
        (
            record
            for record in period_records
            if record["id"] == deleting_id
        ),
        None
    )

    if deleting_record:

        st.divider()

        st.warning(
            "Are you sure you want to delete this work record?"
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:

            if st.button(
                "Yes, Delete",
                key=f"confirm_delete_{deleting_id}",
                use_container_width=True
            ):

                try:

                    delete_work_session(
                        deleting_id
                    )

                    del st.session_state.deleting_id

                    st.success(
                        "Work record deleted."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Unable to delete the record."
                    )

                    st.caption(str(e))

        with cancel_col:

            if st.button(
                "Cancel",
                key=f"cancel_delete_{deleting_id}",
                use_container_width=True
            ):

                del st.session_state.deleting_id
                st.rerun()


# =========================================================
# Add Work Record
# =========================================================

st.divider()

with st.expander(
    "＋ Add Work Record",
    expanded=False
):

    st.markdown(
        '<div class="add-title">New Work Record</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_work_form"):

        add_date = st.date_input(
            "Date",
            value=datetime.date.today()
        )

        add_start = st.time_input(
            "Start Time",
            value=datetime.time(5, 0)
        )

        add_end = st.time_input(
            "End Time",
            value=datetime.time(14, 0)
        )

        add_break = st.number_input(
            "Break (minutes)",
            min_value=0,
            max_value=300,
            value=30,
            step=5
        )

        add_notes = st.text_input(
            "Notes",
            placeholder="Optional"
        )

        add_submit = st.form_submit_button(
            "Add Record",
            use_container_width=True
        )

        if add_submit:

            try:

                if add_end == add_start:

                    st.error(
                        "Start time and end time cannot be the same."
                    )

                else:

                    add_work_session(
                        add_date,
                        add_start,
                        add_end,
                        add_break,
                        add_notes
                    )

                    st.success(
                        "Work record added."
                    )

                    st.rerun()

            except Exception as e:

                st.error(
                    "Unable to add the work record."
                )

                st.caption(str(e))


# =========================================================
# Previous Work History
# =========================================================

try:

    all_records = get_work_history()

except Exception as e:

    all_records = []
    st.error(
        "Unable to load work history from Supabase."
    )
    st.caption(str(e))


previous_records = []

for record in all_records:

    record_date = datetime.date.fromisoformat(
        record["work_date"]
    )

    if not (
        start_date <= record_date <= end_date
    ):
        previous_records.append(record)


st.divider()

with st.expander(
    f"📚 Work History ({len(previous_records)})",
    expanded=False
):

    if not previous_records:

        st.caption(
            "No previous records."
        )

    else:

        for record in previous_records:

            work_date = datetime.date.fromisoformat(
                record["work_date"]
            )

            start_time = datetime.time.fromisoformat(
                normalize_time(record["start_time"])
            )

            end_time = datetime.time.fromisoformat(
                normalize_time(record["end_time"])
            )

            hours = float(
                record.get("total_hours", 0) or 0
            )

            break_minutes = int(
                record.get("break_minutes", 0) or 0
            )

            notes = record.get("notes")

            st.markdown(
                f"""
                <div class="record-card">

                    <div class="record-header">

                        <div class="record-date">
                            {format_date(work_date)}
                        </div>

                        <div class="record-hours">
                            {hours:.2f} h
                        </div>

                    </div>

                    <div class="record-time">
                        {format_time(start_time)}
                        →
                        {format_time(end_time)}
                    </div>

                    <div class="record-detail">
                        Break: {break_minutes} min
                    </div>

                    {
                        f'<div class="record-detail">Notes: {notes}</div>'
                        if notes
                        else ""
                    }

                </div>
                """,
                unsafe_allow_html=True,
            )
