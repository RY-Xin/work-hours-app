import streamlit as st
import sqlite3
from datetime import datetime, date, time, timedelta


DB_NAME = "work_hours.db"

# =========================================================
# Pay Period Settings
# =========================================================

# Your company's pay period:
# Aug 24 - Sep 6, 2026
PAY_PERIOD_START = date(2026, 8, 24)

PAY_PERIOD_LENGTH = 14


# =========================================================
# Database
# =========================================================

def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS work_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            break_minutes INTEGER DEFAULT 0,
            total_hours REAL NOT NULL,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_work_session(
    work_date,
    start_time,
    end_time,
    break_minutes,
    total_hours,
    notes
):
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT INTO work_sessions
        (
            work_date,
            start_time,
            end_time,
            break_minutes,
            total_hours,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        work_date,
        start_time,
        end_time,
        break_minutes,
        total_hours,
        notes
    ))

    conn.commit()
    conn.close()


def get_work_history():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            work_date,
            start_time,
            end_time,
            break_minutes,
            total_hours,
            notes
        FROM work_sessions
        ORDER BY work_date DESC, start_time DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def get_period_records(period_start, period_end):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            work_date,
            start_time,
            end_time,
            break_minutes,
            total_hours,
            notes
        FROM work_sessions
        WHERE work_date >= ?
          AND work_date <= ?
        ORDER BY work_date ASC, start_time ASC
    """, (
        period_start.strftime("%Y-%m-%d"),
        period_end.strftime("%Y-%m-%d")
    ))

    records = cursor.fetchall()

    conn.close()

    return records


def update_work_session(
    record_id,
    work_date,
    start_time,
    end_time,
    break_minutes,
    total_hours,
    notes
):
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        UPDATE work_sessions
        SET
            work_date = ?,
            start_time = ?,
            end_time = ?,
            break_minutes = ?,
            total_hours = ?,
            notes = ?
        WHERE id = ?
    """, (
        work_date,
        start_time,
        end_time,
        break_minutes,
        total_hours,
        notes,
        record_id
    ))

    conn.commit()
    conn.close()


def delete_work_session(record_id):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        DELETE FROM work_sessions
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()


# =========================================================
# Calculate Hours
# =========================================================

def calculate_hours(start_time, end_time, break_minutes):

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

    period_number = days_since_start // PAY_PERIOD_LENGTH

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


def format_period(period_start, period_end):

    return (
        f"{period_start.strftime('%b %d')} "
        f"– "
        f"{period_end.strftime('%b %d, %Y')}"
    )


# =========================================================
# App Initialization
# =========================================================

init_db()

st.title("⏱ Work Hours Tracker")


# =========================================================
# Pay Period Navigation
# =========================================================

today = date.today()

# Initialize selected pay period
if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0


# Get current pay period
current_start, current_end = get_pay_period(today)


# Apply navigation offset
selected_start = (
    current_start
    + timedelta(
        days=st.session_state.period_offset
        * PAY_PERIOD_LENGTH
    )
)

selected_end = (
    selected_start
    + timedelta(days=PAY_PERIOD_LENGTH - 1)
)


st.subheader("Pay Period")


# Navigation buttons

left_col, middle_col, right_col = st.columns(
    [1, 2, 1]
)


with left_col:

    if st.button("← Previous"):

        st.session_state.period_offset -= 1

        st.rerun()


with middle_col:

    st.markdown(
        f"<h3 style='text-align: center;'>"
        f"{format_period(selected_start, selected_end)}"
        f"</h3>",
        unsafe_allow_html=True
    )


with right_col:

    if st.button("Next →"):

        st.session_state.period_offset += 1

        st.rerun()


# Return to current period

if st.session_state.period_offset != 0:

    if st.button("Today / Current Period"):

        st.session_state.period_offset = 0

        st.rerun()


# =========================================================
# Pay Period Summary
# =========================================================

period_records = get_period_records(
    selected_start,
    selected_end
)

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
# Daily Hours for Selected Pay Period
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


# Preview total hours

total_hours = calculate_hours(
    start_time,
    end_time,
    break_minutes
)


st.metric(
    "Total Hours",
    f"{total_hours:.2f} hours"
)


if st.button(
    "Add Record",
    type="primary"
):

    add_work_session(
        work_date.strftime("%Y-%m-%d"),
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


# =========================================================
# Full Work History
# =========================================================

st.divider()

st.subheader("Work History")


records = get_work_history()


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


            # Edit

            if col4.button(
                "✏️",
                key=f"edit_{record_id}"
            ):

                st.session_state.editing_id = record_id

                st.rerun()


            # Delete

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


                if save_col.button(
                    "Save Changes",
                    key=f"save_{record_id}",
                    type="primary"
                ):

                    update_work_session(
                        record_id,
                        edit_date.strftime("%Y-%m-%d"),
                        edit_start.strftime("%H:%M"),
                        edit_end.strftime("%H:%M"),
                        edit_break,
                        edit_total,
                        edit_notes
                    )

                    st.session_state.editing_id = None

                    st.rerun()


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


                if delete_col.button(
                    "Yes, Delete",
                    key=f"confirm_delete_{record_id}"
                ):

                    delete_work_session(
                        record_id
                    )

                    st.session_state.deleting_id = None

                    st.rerun()


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