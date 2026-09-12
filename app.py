import streamlit as st
import datetime
import html
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

:root {
    --bg: #faf8f5;
    --card: #fffdfb;
    --text: #514a46;
    --text-light: #8a817b;
    --border: #eee7e1;

    --yellow: #f6edc9;
    --yellow-dark: #eadc9d;

    --pink: #f6dfe1;
    --pink-dark: #eac5c9;

    --peach: #f7dfcf;
    --peach-dark: #edc8ad;

    --danger: #f3d7d7;
    --danger-text: #9a6868;
}


/* =========================================================
   Page
   ========================================================= */

.stApp {
    background: var(--bg);
}

.block-container {
    max-width: 680px;
    padding-top: 4rem;
    padding-bottom: 3rem;
    padding-left: 16px;
    padding-right: 16px;
}


/* Hide Streamlit menu/footer */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* =========================================================
   Header
   ========================================================= */

.app-title {
    color: var(--text);
    font-size: 30px;
    font-weight: 750;
    letter-spacing: -0.5px;
    margin-bottom: 1px;
}

.app-subtitle {
    color: var(--text-light);
    font-size: 14px;
    margin-bottom: 20px;
}


/* =========================================================
   Pay Period
   ========================================================= */

.period-label {
    text-align: center;
    color: var(--text-light);
    font-size: 12px;
    font-weight: 500;
    margin-top: 4px;
}

.period-title {
    text-align: center;
    color: var(--text);
    font-size: 17px;
    font-weight: 700;
    margin-top: 2px;
}


/* Navigation buttons */

.stButton > button {
    border-radius: 12px;
    border: 1px solid var(--border);
    background: #fffdfb;
    color: var(--text);
    font-size: 13px;
    font-weight: 550;
    min-height: 38px;
    transition: 0.15s ease;
}

.stButton > button:hover {
    border-color: var(--yellow-dark);
    color: var(--text);
    background: #fffaf0;
}


/* =========================================================
   Summary Card
   ========================================================= */

.summary-card {
    background: var(--yellow);
    border: 1px solid #eee3bd;
    border-radius: 20px;
    padding: 21px 22px;
    margin-top: 18px;
    margin-bottom: 16px;
}

.summary-label {
    color: #81785d;
    font-size: 13px;
    font-weight: 550;
}

.summary-value {
    color: var(--text);
    font-size: 36px;
    line-height: 1.1;
    font-weight: 750;
    letter-spacing: -0.5px;
    margin-top: 2px;
}

.summary-secondary {
    color: #81785d;
    font-size: 14px;
    margin-top: 6px;
}


/* =========================================================
   Add Work Record
   ========================================================= */

.add-section {
    background: var(--pink);
    border: 1px solid #ecd0d3;
    border-radius: 17px;
    padding: 2px 14px;
    margin-bottom: 16px;
}


/* Expander */

[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--card);
    overflow: hidden;
}

[data-testid="stExpander"] details summary {
    color: var(--text);
    font-weight: 650;
}


/* Add form button */

.add-form-button button {
    background: var(--peach) !important;
    border: 1px solid var(--peach-dark) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
}

.add-form-button button:hover {
    background: #f4d5bf !important;
}


/* =========================================================
   Section Titles
   ========================================================= */

.section-title {
    color: var(--text);
    font-size: 19px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 10px;
}


/* =========================================================
   Daily Hours Expander
   ========================================================= */

.daily-expander {
    margin-top: 4px;
}


/* =========================================================
   Record Card
   ========================================================= */

.record-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 15px 16px;
    margin-bottom: 6px;
    box-shadow: 0 1px 5px rgba(90, 75, 65, 0.035);
}

.record-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.record-date {
    color: var(--text);
    font-size: 15px;
    font-weight: 680;
}

.record-hours {
    color: var(--text);
    font-size: 16px;
    font-weight: 720;
    white-space: nowrap;
}

.record-time {
    color: #625a55;
    font-size: 14px;
    margin-top: 7px;
}

.record-detail {
    color: var(--text-light);
    font-size: 12px;
    margin-top: 4px;
}


/* =========================================================
   Edit / Delete Buttons
   ========================================================= */

.edit-delete-row .stButton > button {
    min-height: 30px;
    height: 30px;
    padding: 0 10px;
    font-size: 12px;
    border-radius: 9px;
    box-shadow: none;
}

.edit-button .stButton > button {
    background: #faf0d2 !important;
    border: 1px solid #eee0b8 !important;
    color: #766a4c !important;
}

.edit-button .stButton > button:hover {
    background: #f5e8c0 !important;
}

.delete-button .stButton > button {
    background: var(--danger) !important;
    border: 1px solid #eac7c7 !important;
    color: var(--danger-text) !important;
}

.delete-button .stButton > button:hover {
    background: #efcece !important;
}


/* =========================================================
   Forms
   ========================================================= */

div[data-testid="stForm"] {
    border: none;
    padding: 0;
}

label {
    color: var(--text) !important;
}

input,
textarea {
    border-radius: 10px !important;
}


/* Primary form button */

div[data-testid="stFormSubmitButton"] button {
    background: var(--peach) !important;
    border: 1px solid var(--peach-dark) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    border-radius: 11px !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background: #f3d3bc !important;
}


/* =========================================================
   Empty State
   ========================================================= */

.empty-message {
    color: var(--text-light);
    background: #fffdfb;
    border: 1px dashed var(--border);
    border-radius: 14px;
    padding: 15px;
    text-align: center;
    font-size: 13px;
}


/* =========================================================
   Mobile
   ========================================================= */

@media (max-width: 600px) {

    .block-container {
        padding-top: 3.5rem;
        padding-left: 13px;
        padding-right: 13px;
    }

    .app-title {
        font-size: 27px;
    }

    .app-subtitle {
        font-size: 13px;
        margin-bottom: 17px;
    }

    .period-title {
        font-size: 16px;
    }

    .summary-card {
        padding: 18px 19px;
        border-radius: 18px;
        margin-top: 15px;
    }

    .summary-value {
        font-size: 32px;
    }

    .record-card {
        padding: 14px 15px;
    }

    .record-date {
        font-size: 14px;
    }

    .record-hours {
        font-size: 15px;
    }

    .record-time {
        font-size: 13px;
    }

    .record-detail {
        font-size: 12px;
    }

    .stButton > button {
        min-height: 36px;
        font-size: 12px;
    }

}


/* =========================================================
   Remove unnecessary vertical gaps
   ========================================================= */

div[data-testid="stVerticalBlock"] > div {
    gap: 0.35rem;
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
    if value is None:
        return None

    return str(value)[:5]


def calculate_hours(start_time, end_time, break_minutes):

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

    total_minutes = (
        end - start
    ).total_seconds() / 60

    total_minutes -= break_minutes

    return max(total_minutes / 60, 0)


def format_date(value):

    if isinstance(value, str):
        value = datetime.date.fromisoformat(value)

    return value.strftime("%a, %b %d")


def format_time(value):

    if isinstance(value, str):
        value = datetime.time.fromisoformat(value)

    return value.strftime("%I:%M %p").lstrip("0")


def get_pay_period(offset=0):

    today = datetime.date.today()

    days_since_start = (
        today - PAY_PERIOD_START
    ).days

    current_period_index = (
        days_since_start // PAY_PERIOD_LENGTH
    )

    period_index = (
        current_period_index + offset
    )

    start_date = (
        PAY_PERIOD_START
        + datetime.timedelta(
            days=period_index * PAY_PERIOD_LENGTH
        )
    )

    end_date = (
        start_date
        + datetime.timedelta(
            days=PAY_PERIOD_LENGTH - 1
        )
    )

    return start_date, end_date


# =========================================================
# Database Functions
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

    supabase.table(
        "work_sessions"
    ).insert(data).execute()


def get_period_records(
    start_date,
    end_date
):

    response = (
        supabase
        .table("work_sessions")
        .select("*")
        .gte(
            "work_date",
            start_date.isoformat()
        )
        .lte(
            "work_date",
            end_date.isoformat()
        )
        .order(
            "work_date",
            desc=False
        )
        .order(
            "start_time",
            desc=False
        )
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

st.html(
    """
<div class="app-title">⏱️ Work Hours</div>
<div class="app-subtitle">
    Simple work time tracking
</div>
"""
)


# =========================================================
# Pay Period Navigation
# =========================================================

if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0


nav_left, nav_center, nav_right = st.columns(
    [1, 2, 1]
)


with nav_left:

    if st.button(
        "‹ Previous",
        use_container_width=True
    ):

        st.session_state.period_offset -= 1
        st.rerun()


with nav_center:

    start_date, end_date = get_pay_period(
        st.session_state.period_offset
    )

    st.html(
        f"""
<div class="period-label">
Pay Period
</div>

<div class="period-title">
{start_date.strftime("%b %d")}
–
{end_date.strftime("%b %d, %Y")}
</div>
"""
    )


with nav_right:

    if st.button(
        "Next ›",
        use_container_width=True
    ):

        st.session_state.period_offset += 1
        st.rerun()


# =========================================================
# Load Current Period
# =========================================================

try:

    period_records = get_period_records(
        start_date,
        end_date
    )

except Exception as e:

    st.error(
        "Unable to load work records from Supabase."
    )

    st.caption(str(e))

    st.stop()


# =========================================================
# Calculate Summary
# =========================================================

total_hours = sum(
    float(
        record.get(
            "total_hours",
            0
        ) or 0
    )
    for record in period_records
)

days_worked = len(period_records)


# =========================================================
# Total Hours
# =========================================================

st.html(
    f"""
<div class="summary-card">

<div class="summary-label">
Total Hours
</div>

<div class="summary-value">
{total_hours:.2f} h
</div>

<div class="summary-secondary">
{days_worked}
{"day" if days_worked == 1 else "days"} worked
</div>

</div>
"""
)


# =========================================================
# Add Work Record
# =========================================================

with st.expander(
    "＋  Add Work Record",
    expanded=False
):

    st.html(
        """
<div class="section-title">
New Work Record
</div>
"""
    )

    with st.form("add_work_form"):

        add_date = st.date_input(
            "Date",
            value=datetime.date.today()
        )

        # Start / End on the same row

        time_col1, time_col2 = st.columns(2)

        with time_col1:

            add_start = st.time_input(
                "Start Time",
                value=datetime.time(5, 0)
            )

        with time_col2:

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

            if add_end == add_start:

                st.error(
                    "Start time and end time cannot be the same."
                )

            else:

                try:

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
# Daily Hours
# =========================================================

with st.expander(
    f"🕐  Daily Hours  ·  {days_worked} days",
    expanded=False
):

    if not period_records:

        st.html(
            """
<div class="empty-message">
No work records for this pay period yet.
</div>
"""
        )

    else:

        for record in period_records:

            work_date = datetime.date.fromisoformat(
                record["work_date"]
            )

            start_time = datetime.time.fromisoformat(
                normalize_time(
                    record["start_time"]
                )
            )

            end_time = datetime.time.fromisoformat(
                normalize_time(
                    record["end_time"]
                )
            )

            hours = float(
                record.get(
                    "total_hours",
                    0
                ) or 0
            )

            break_minutes = int(
                record.get(
                    "break_minutes",
                    0
                ) or 0
            )

            notes = record.get("notes")

            notes_html = ""

            if notes:

                safe_notes = html.escape(
                    str(notes)
                )

                notes_html = (
                    f'<div class="record-detail">'
                    f'Notes: {safe_notes}'
                    f'</div>'
                )

            st.html(
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
&nbsp;→&nbsp;
{format_time(end_time)}
</div>

<div class="record-detail">
Break {break_minutes} min
</div>

{notes_html}

</div>
"""
            )

            # Small Edit / Delete buttons

            edit_col, delete_col, spacer = st.columns(
                [0.8, 0.8, 3.4]
            )

            with edit_col:

                st.markdown(
                    '<div class="edit-button">',
                    unsafe_allow_html=True
                )

                if st.button(
                    "✏ Edit",
                    key=f"edit_{record['id']}",
                    use_container_width=True
                ):

                    st.session_state.editing_id = (
                        record["id"]
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            with delete_col:

                st.markdown(
                    '<div class="delete-button">',
                    unsafe_allow_html=True
                )

                if st.button(
                    "Delete",
                    key=f"delete_{record['id']}",
                    use_container_width=True
                ):

                    st.session_state.deleting_id = (
                        record["id"]
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# =========================================================
# Edit Work Record
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

        st.html(
            """
<div class="section-title">
Edit Work Record
</div>
"""
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
            editing_record.get(
                "break_minutes",
                0
            ) or 0
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

            edit_time_col1, edit_time_col2 = st.columns(2)

            with edit_time_col1:

                new_start = st.time_input(
                    "Start Time",
                    value=edit_start
                )

            with edit_time_col2:

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

    deleting_id = (
        st.session_state.deleting_id
    )

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
            "Delete this work record?"
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
