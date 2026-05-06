from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import random







def student_required():
    return "user_id" in session and session.get("role") == "student"

def advisor_required():
    return "user_id" in session and session.get("role") == "advisor"


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

# for sessions
app.secret_key = "62a758d4-460c-4220-b277-693f0502d1da"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["MentorVerseDB"]
reset_pins = {}



# students and advisors
students = db["students"]
advisors = db["advisors"]

from bson.objectid import ObjectId

def student_required():
    return "user_id" in session and session.get("role") == "student"

def advisor_required():
    return "user_id" in session and session.get("role") == "advisor"


def get_logged_user():
    if "user_id" not in session:
        return None

    user_id = session["user_id"]

    if session.get("role") == "student":
        return students.find_one({"_id": ObjectId(user_id)})
    else:
        return advisors.find_one({"_id": ObjectId(user_id)})








@app.route("/")
def home():
    return render_template("Home-page.html")







# puplic pages

@app.route("/Home-page/")
def home_page():
    return render_template("Home-page.html")


@app.route("/faq-page/")
def faq_page():
    return render_template("faq-page.html")


@app.route("/contact-us-page/")
def contact_us_page():
    return render_template("contact-us-page.html")


@app.route("/about-us-page/")
def about_us_page():
    return render_template("about-us-page.html")


@app.route("/error-page/")
def error_page():
    return render_template("error-page.html")






# authentication pages  


@app.route("/login-page/", methods=["GET", "POST"])
def login_page():
        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role")

            if role == "advisor":
                user = advisors.find_one({"email": email})
            else:
                user = students.find_one({"email": email})

            if not user:
                flash("User not found")
                return redirect(url_for("login_page"))

            if not check_password_hash(user["password"], password):
                flash("Incorrect password")
                return redirect(url_for("login_page"))

            # create session
            session["user_id"] = str(user["_id"])
            session["email"] = user["email"]
            session["role"] = user["role"]

            # redirect based on role
            if role == "student":
                return redirect(url_for("student_dashboard_page"))
            else:
                return redirect(url_for("advisor_students_list_page"))

        return render_template("login-page.html")






@app.route("/register-page/", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":

        print(request) 


        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        university_id = request.form.get("universityID")
        password = request.form.get("password")
        role = request.form.get("role")

        if not firstname or not lastname or not email or not university_id or not password:
            flash("Please fill all fields")
            return redirect(url_for("register_page"))

        existing_user = students.find_one({"$or": 
            [
                {"email": email},
                {"student_id": university_id}
            ]
        })

        if existing_user:
            flash("User already exists")
            return redirect(url_for("register_page"))


        test_students = db["test_student"]
        student_user = test_students.find_one({"sid": "1"})
        test_advisors = db["test_advisor"]
        advisor_user  = test_advisors.find_one({"aid": "1"})

        if role == "advisor":

            user = {
                "aid": "test",
                "Fname": firstname,
                "Lname": lastname,
                "email": email,
                "university_id": university_id,
                "password": generate_password_hash(password),
                "role": role,  
                "department": advisor_user.get("department", []),
                "advisor_students": advisor_user.get("advisor_students", []),
                "office": advisor_user.get("office", []),
                "bio": advisor_user.get("bio", []),
                "gender": advisor_user.get("gender", []),
                "notifications": advisor_user.get("notifications", [])
            }

            advisors.insert_one(user)

        else:

            user = {
                "sid": "test",
                "Fname": firstname,
                "Lname": lastname,
                "email": email,
                "password": generate_password_hash(password),
                "student_id": university_id,
                "bio": student_user.get("bio", []),
                "gender": student_user.get("gender", []),
                "Target_GPA": student_user.get("Target_GPA", []),
                "Phone_Number": student_user.get("Phone_Number", []),
                "role": role,
                "major": student_user.get("major", []),
                "advisor_id": "MohammedAli@jazan.edu.sa",
                "cumulative_gpa": student_user.get("cumulative_gpa", []),
                "transcript": student_user.get("transcript", []),
                "schedule": student_user.get("schedule", []),
                "advisor_recommendations": student_user.get("advisor_recommendations", []),
                "ai_recommendations": student_user.get("ai_recommendations", []),
                "notifications": student_user.get("notifications", [])
            }

            students.insert_one(user)

        print(user)  

        return redirect(url_for("login_page"))
    return render_template("register-page.html")





@app.route("/forgot-password-page/", methods=["GET", "POST"])
def forgot_password_page():

    step = session.get("step", "email")

    if request.method == "POST":

        # STEP 1: SEND OTP

        if step == "email":
            email = request.form.get("email")

            student_user = students.find_one({"email": email})
            advisor_user = advisors.find_one({"email": email})

            user = student_user or advisor_user
            
            if not user:
                flash("No account found with this email")
                return redirect(url_for("forgot_password_page"))

            # generate 4-digit PIN
            pin = str(random.randint(1000, 9999))
            reset_pins[email] = pin

            print("OTP (for testing):", pin)  

            # send email
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login("mentorverseplatform@gmail.com", "ieyw gpbe zlmz hsir")

                message = f"Subject: MentorVerse Code\n\nYour verification code is: {pin}"
                server.sendmail("mentorverseplatform@gmail.com", email, message)
                server.quit()

            except Exception as e:
                print("EMAIL ERROR:", e)
                flash("Failed to send email")
                return redirect(url_for("forgot_password_page"))

            session["reset_email"] = email
            session["step"] = "otp"

            flash("Verification code sent to your email")
            return redirect(url_for("forgot_password_page"))

        # STEP 2: VERIFY OTP

        elif step == "otp":
            entered_pin = request.form.get("pin")
            email = session.get("reset_email")

            if not email:
                return redirect(url_for("forgot_password_page"))

            if reset_pins.get(email) != entered_pin:
                flash("Invalid verification code")
                return redirect(url_for("forgot_password_page"))

            session["step"] = "reset"
            return redirect(url_for("forgot_password_page"))

        # STEP 3: RESET PASSWORD

        elif step == "reset":
            email = session.get("reset_email")
            password = request.form.get("password")

            if not email:
                return redirect(url_for("forgot_password_page"))

            hashed_password = generate_password_hash(password)

            if students.find_one({"email": email}):
                students.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password}}
                )
            
            elif advisors.find_one({"email": email}):
                advisors.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password}}
                )

            # cleanup
            reset_pins.pop(email, None)
            session.clear()

            flash("Password updated successfully")
            return redirect(url_for("login_page"))

    return render_template(
        "forgot-password-page.html",
        step=session.get("step", "email")
    )




@app.route("/logout/", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))




## private pages ##
# student pages  

@app.route("/student-dashboard-page/", methods=["GET", "POST"])
def student_dashboard_page():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    #user = students.find_one({"email": session["email"]})

    # Visuals



    user = get_logged_user()

    return render_template("student-dashboard-page.html", user=user)




@app.route("/student-transcript-page/")
def student_transcript_page():
    if not student_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    transcript = user.get("transcript", [])

    total_credits = 0
    completed_courses = 0

    for semester in transcript:
        for course in semester.get("courses", []):
            if course.get("grade") != "NG":
                total_credits += course.get("credits", 0)
                completed_courses += 1

    last_semester = transcript[-2] if transcript else {}
    academic_standing = last_semester.get("academic_standing", "N/A")
    last_semester_gpa = last_semester.get("semester_gpa", 0)
    
    completed_semesters = len(transcript)

    if completed_semesters <= 2:
        level = "Freshman Year"

    elif completed_semesters <= 4:
        level = "Sophomore Year"

    elif completed_semesters <= 6:
        level = "Junior Year"

    else:
        level = "Senior Year"

    return render_template(
        "student-transcript-page.html",
        user=user,
        transcript=transcript,
        total_credits=total_credits,
        completed_courses=completed_courses,
        academic_standing=academic_standing,
        last_semester_gpa=last_semester_gpa,
        level=level
    )





@app.route("/student-schedule-page/")
def student_schedule_page():

    if not student_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    schedule = user.get("schedule", [])


    today_classes = len([
        item for item in schedule
        if item["day"] == "Sunday"
    ])


    week_hours = len(schedule)

  
    next_class = schedule[0] if schedule else None


    free_slots = max(0, 20 - len(schedule))


    return render_template(
        "student-schedule-page.html",
        user=user,
        schedule=schedule,
        today_classes=today_classes,
        week_hours=week_hours,
        next_class=next_class,
        free_slots=free_slots
    )






@app.route("/student-notification-page/")
def student_notification_page():

    if not student_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    notifications = user.get("notifications", [])

    return render_template(
        "student-notification-page.html",
        user=user,
        notifications=notifications
    )





@app.route("/student-settings-page/", methods=["GET", "POST"])
def student_settings_page():

    if not student_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    if request.method == "POST":

        fname = request.form.get("first_name")
        lname = request.form.get("last_name")
        Phone_Number = request.form.get("Phone_Number")
        bio = request.form.get("bio")
        Target_GPA = request.form.get("Target_GPA")

        students.update_one(
            {"email": user["email"]},
            {"$set": {
                "Fname": fname,
                "Lname": lname,
                "Phone_Number": Phone_Number,
                "bio": bio,
                "Target_GPA": Target_GPA
            }}
        )

        flash("student profile updated successfully")
        return redirect(url_for("student_settings_page"))

    return render_template(
        "student-settings-page.html",
        user=user
    )





# advisor pages
@app.route("/advisor-students-list-page/")
def advisor_students_list_page():
    if not advisor_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()
    students_list = list(students.find())

    return render_template(
        "advisor-students-list-page.html",
        user=user,
        students=students_list
    )





@app.route("/advisor-student-performance-cards/")
def advisor_student_performance_cards():
    if not advisor_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    return render_template(
        "advisor-student-performance-cards.html",
        user=user
    )





@app.route("/advisor-student-performance-page/")
def advisor_student_performance_page():
    if not advisor_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    return render_template(
        "advisor-student-performance-page.html",
        user=user
    )






@app.route("/advisor-notification-page/")
def advisor_notification_page():
    if not advisor_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    notifications = user.get("notifications", [])

    return render_template(
        "advisor-notification-page.html",
        user=user,
        notifications=notifications
    )




@app.route("/advisor-settings-page/", methods=["GET", "POST"])
def advisor_settings_page():

    if not advisor_required():
        return redirect(url_for("login_page"))

    user = get_logged_user()

    if request.method == "POST":

        fname = request.form.get("first_name")
        lname = request.form.get("last_name")
        department = request.form.get("department")
        bio = request.form.get("bio")
        office = request.form.get("office")

        advisors.update_one(
            {"email": user["email"]},
            {"$set": {
                "Fname": fname,
                "Lname": lname,
                "department": department,
                "bio": bio,
                "office": office
            }}
        )

        flash("Advisor profile updated successfully")
        return redirect(url_for("advisor_settings_page"))

    return render_template(
        "advisor-settings-page.html",
        user=user
    )




# admin page
@app.route("/admin-page/")
def admin_page():

    return render_template("admin-page.html" )









if __name__ == "__main__":
    app.run(debug=True) 