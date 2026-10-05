import streamlit as st
import pandas as pd
import os
import pickle
import face_recognition

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Smart Attendance and Academic Analytics System")

# CREATE FOLDERS
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("attendance", exist_ok=True)
os.makedirs("images", exist_ok=True)

# FILE PATHS
STUDENT_FILE = "data/students.csv"
ATTENDANCE_FILE = "attendance/attendance.csv"
FACE_FILE = "models/face_encodings.pkl"


# =================================================
# LOAD STUDENTS
# =================================================

def load_students():

    if not os.path.exists(STUDENT_FILE):

        return pd.DataFrame(
            columns=[
                "Name",
                "Roll Number",
                "Department",
                "Year"
            ]
        )

    try:

        return pd.read_csv(STUDENT_FILE)

    except pd.errors.EmptyDataError:

        return pd.DataFrame(
            columns=[
                "Name",
                "Roll Number",
                "Department",
                "Year"
            ]
        )


# =================================================
# LOAD ATTENDANCE
# =================================================

def load_attendance():

    if not os.path.exists(ATTENDANCE_FILE):

        return pd.DataFrame(
            columns=[
                "Name",
                "Date",
                "Status"
            ]
        )

    try:

        return pd.read_csv(ATTENDANCE_FILE)

    except pd.errors.EmptyDataError:

        return pd.DataFrame(
            columns=[
                "Name",
                "Date",
                "Status"
            ]
        )


# =================================================
# LOAD FACE DATA
# =================================================

def load_face_data():

    if os.path.exists(FACE_FILE):

        with open(FACE_FILE, "rb") as file:

            return pickle.load(file)

    return {}


# =================================================
# SAVE FACE DATA
# =================================================

def save_face_data(face_data):

    with open(FACE_FILE, "wb") as file:

        pickle.dump(face_data, file)


# =================================================
# SIDEBAR
# =================================================

st.sidebar.title("📚 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Student Registration",
        "Face Registration",
        "Attendance",
        "Attendance History",
        "Academic Analytics",
        "Student Search"
    ]
)


# =================================================
# DASHBOARD
# =================================================

if page == "Dashboard":

    st.header("📊 Dashboard")

    students = load_students()
    attendance = load_attendance()

    total_students = len(students)

    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    if not attendance.empty:

        present_today = len(
            attendance[
                (attendance["Date"].astype(str) == today)
                &
                (attendance["Status"] == "Present")
            ]
        )

    else:

        present_today = 0

    if total_students > 0:

        attendance_percentage = (
            present_today / total_students
        ) * 100

    else:

        attendance_percentage = 0

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👩‍🎓 Total Students",
            total_students
        )

    with col2:

        st.metric(
            "✅ Present Today",
            present_today
        )

    with col3:

        st.metric(
            "📊 Attendance Percentage",
            f"{attendance_percentage:.1f}%"
        )

    st.subheader("📋 Registered Students")

    if not students.empty:

        st.dataframe(
            students,
            use_container_width=True
        )

    else:

        st.info(
            "No students registered yet."
        )


# =================================================
# STUDENT REGISTRATION
# =================================================

elif page == "Student Registration":

    st.header("👩‍🎓 Student Registration")

    name = st.text_input(
        "Student Name"
    )

    roll_number = st.text_input(
        "Roll Number"
    )

    department = st.text_input(
        "Department"
    )

    year = st.selectbox(
        "Year",
        [
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year"
        ]
    )

    if st.button("Register Student"):

        if name and roll_number and department:

            students = load_students()

            if roll_number in students[
                "Roll Number"
            ].astype(str).values:

                st.error(
                    "This roll number is already registered."
                )

            else:

                new_student = pd.DataFrame({

                    "Name": [name],

                    "Roll Number": [roll_number],

                    "Department": [department],

                    "Year": [year]

                })

                students = pd.concat(
                    [
                        students,
                        new_student
                    ],
                    ignore_index=True
                )

                students.to_csv(
                    STUDENT_FILE,
                    index=False
                )

                st.success(
                    "Student registered successfully! ✅"
                )

        else:

            st.warning(
                "Please fill in all required fields."
            )


# =================================================
# FACE REGISTRATION
# =================================================

elif page == "Face Registration":

    st.header("📸 Face Registration")

    st.write(
        "Register a student's face using the webcam."
    )

    students = load_students()

    if students.empty:

        st.warning(
            "Please register a student first."
        )

    else:

        student_names = students[
            "Name"
        ].tolist()

        selected_student = st.selectbox(
            "Select Student",
            student_names
        )

        camera_image = st.camera_input(
            "Take a picture"
        )

        if camera_image is not None:

            image = face_recognition.load_image_file(
                camera_image
            )

            face_locations = (
                face_recognition.face_locations(
                    image
                )
            )

            face_encodings = (
                face_recognition.face_encodings(
                    image,
                    face_locations
                )
            )

            if len(face_encodings) == 0:

                st.error(
                    "No face detected. Please try again."
                )

            elif len(face_encodings) > 1:

                st.error(
                    "Multiple faces detected. "
                    "Please capture only one person."
                )

            else:

                face_data = load_face_data()

                face_data[
                    selected_student
                ] = face_encodings[0]

                save_face_data(
                    face_data
                )

                st.success(
                    f"Face registered successfully "
                    f"for {selected_student}! ✅"
                )


# =================================================
# ATTENDANCE
# =================================================

elif page == "Attendance":

    st.header("✅ Attendance")

    students = load_students()

    if students.empty:

        st.warning(
            "Please register students first."
        )

    else:

        student_names = students[
            "Name"
        ].tolist()

        selected_student = st.selectbox(
            "Select Student",
            student_names
        )

        if st.button("Mark Present"):

            today = pd.Timestamp.now().strftime(
                "%Y-%m-%d"
            )

            attendance = load_attendance()

            if not attendance.empty:

                duplicate = (
                    (attendance["Name"] == selected_student)
                    &
                    (
                        attendance["Date"].astype(str)
                        == today
                    )
                )

            else:

                duplicate = pd.Series(
                    dtype=bool
                )

            if duplicate.any():

                st.warning(
                    f"{selected_student} is already "
                    "marked present today."
                )

            else:

                new_attendance = pd.DataFrame({

                    "Name": [selected_student],

                    "Date": [today],

                    "Status": ["Present"]

                })

                attendance = pd.concat(
                    [
                        attendance,
                        new_attendance
                    ],
                    ignore_index=True
                )

                attendance.to_csv(
                    ATTENDANCE_FILE,
                    index=False
                )

                st.success(
                    f"{selected_student} marked Present! ✅"
                )

    st.subheader(
        "📋 Attendance Records"
    )

    attendance = load_attendance()

    if not attendance.empty:

        st.dataframe(
            attendance,
            use_container_width=True
        )

    else:

        st.info(
            "No attendance records yet."
        )


# =================================================
# ATTENDANCE HISTORY
# =================================================

elif page == "Attendance History":

    st.header("📅 Attendance History")

    students = load_students()
    attendance = load_attendance()

    if students.empty:

        st.info(
            "Please register students first."
        )

    elif attendance.empty:

        st.info(
            "No attendance records available yet."
        )

    else:

        # Convert dates safely
        attendance["Date"] = pd.to_datetime(
            attendance["Date"],
            errors="coerce"
        )

        # Remove invalid dates
        attendance = attendance.dropna(
            subset=["Date"]
        )

        if attendance.empty:

            st.info(
                "No valid attendance dates found."
            )

        else:

            # Date selection
            min_date = attendance["Date"].min().date()
            max_date = attendance["Date"].max().date()

            selected_date = st.date_input(
                "📅 Select Attendance Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )

            selected_date = pd.Timestamp(
                selected_date
            )

            # Filter selected date
            date_attendance = attendance[
                attendance["Date"] == selected_date
            ]

            st.subheader(
                f"Attendance for {selected_date.strftime('%d-%m-%Y')}"
            )

            # Count present students
            present_count = len(
                date_attendance[
                    date_attendance["Status"]
                    == "Present"
                ]
            )

            total_students = len(students)

            if total_students > 0:

                attendance_percentage = (
                    present_count
                    / total_students
                    * 100
                )

            else:

                attendance_percentage = 0

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "👩‍🎓 Total Students",
                    total_students
                )

            with col2:

                st.metric(
                    "✅ Present",
                    present_count
                )

            with col3:

                st.metric(
                    "📊 Attendance",
                    f"{attendance_percentage:.1f}%"
                )

            # Display records
            st.subheader(
                "📋 Students Present"
            )

            if not date_attendance.empty:

                display_data = date_attendance.copy()

                display_data["Date"] = (
                    display_data["Date"]
                    .dt.strftime("%Y-%m-%d")
                )

                st.dataframe(
                    display_data,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No attendance was marked "
                    "for this date."
                )

            # Complete attendance history
            st.subheader(
                "📚 Complete Attendance History"
            )

            complete_history = attendance.copy()

            complete_history["Date"] = (
                complete_history["Date"]
                .dt.strftime("%Y-%m-%d")
            )

            st.dataframe(
                complete_history,
                use_container_width=True
            )


# =================================================
# ACADEMIC ANALYTICS
# =================================================

elif page == "Academic Analytics":

    st.header("📈 Academic Analytics")

    students = load_students()
    attendance = load_attendance()

    if students.empty:

        st.info(
            "Register students first to view analytics."
        )

    else:

        if not attendance.empty:

            total_days = (
                attendance["Date"]
                .astype(str)
                .nunique()
            )

        else:

            total_days = 0

        analytics = students[
            [
                "Name",
                "Roll Number",
                "Department",
                "Year"
            ]
        ].copy()

        if not attendance.empty:

            present_counts = (
                attendance[
                    attendance["Status"]
                    == "Present"
                ]
                .groupby("Name")
                .size()
            )

        else:

            present_counts = pd.Series(
                dtype=int
            )

        analytics["Days Present"] = (
            analytics["Name"]
            .map(present_counts)
            .fillna(0)
            .astype(int)
        )

        if total_days > 0:

            analytics[
                "Attendance Percentage"
            ] = (
                analytics["Days Present"]
                / total_days
                * 100
            )

        else:

            analytics[
                "Attendance Percentage"
            ] = 0

        analytics[
            "Attendance Percentage"
        ] = (
            analytics[
                "Attendance Percentage"
            ].round(1)
        )

        def get_status(percentage):

            if percentage >= 75:

                return "Good"

            elif percentage >= 60:

                return "Warning"

            else:

                return "Low"

        analytics["Status"] = (
            analytics[
                "Attendance Percentage"
            ].apply(get_status)
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "👩‍🎓 Total Students",
                len(students)
            )

        with col2:

            st.metric(
                "📅 Total Working Days",
                total_days
            )

        with col3:

            average_attendance = (
                analytics[
                    "Attendance Percentage"
                ].mean()
            )

            st.metric(
                "📊 Average Attendance",
                f"{average_attendance:.1f}%"
            )

        st.subheader(
            "📊 Student Attendance Analysis"
        )

        st.dataframe(
            analytics,
            use_container_width=True
        )

        st.subheader(
            "📈 Attendance Percentage Chart"
        )

        chart_data = analytics[
            [
                "Name",
                "Attendance Percentage"
            ]
        ].set_index("Name")

        st.bar_chart(
            chart_data
        )

        st.subheader(
            "⚠️ Attendance Status"
        )

        for index, row in analytics.iterrows():

            if row["Status"] == "Good":

                st.success(
                    f"{row['Name']}: "
                    f"{row['Attendance Percentage']}% "
                    "— Good attendance ✅"
                )

            elif row["Status"] == "Warning":

                st.warning(
                    f"{row['Name']}: "
                    f"{row['Attendance Percentage']}% "
                    "— Attendance needs improvement ⚠️"
                )

            else:

                st.error(
                    f"{row['Name']}: "
                    f"{row['Attendance Percentage']}% "
                    "— Low attendance ❌"
                )


# =================================================
# STUDENT SEARCH
# =================================================

elif page == "Student Search":

    st.header("🔎 Student Search & Filter")

    students = load_students()

    if students.empty:

        st.info(
            "No students registered yet."
        )

    else:

        st.subheader(
            "Search Student"
        )

        search_text = st.text_input(
            "🔍 Search by name or roll number"
        )

        st.subheader(
            "Filter Students"
        )

        col1, col2 = st.columns(2)

        with col1:

            departments = [
                "All"
            ] + sorted(
                students["Department"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_department = st.selectbox(
                "Department",
                departments
            )

        with col2:

            years = [
                "All"
            ] + sorted(
                students["Year"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_year = st.selectbox(
                "Year",
                years
            )

        filtered_students = students.copy()

        # SEARCH
        if search_text:

            search_text = search_text.lower()

            filtered_students = filtered_students[
                filtered_students["Name"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
                |
                filtered_students["Roll Number"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
            ]

        # DEPARTMENT FILTER
        if selected_department != "All":

            filtered_students = filtered_students[
                filtered_students["Department"]
                .astype(str)
                == selected_department
            ]

        # YEAR FILTER
        if selected_year != "All":

            filtered_students = filtered_students[
                filtered_students["Year"]
                .astype(str)
                == selected_year
            ]

        st.subheader(
            f"📋 Students Found: "
            f"{len(filtered_students)}"
        )

        if not filtered_students.empty:

            st.dataframe(
                filtered_students,
                use_container_width=True
            )

        else:

            st.warning(
                "No students match your search or filters."
            )