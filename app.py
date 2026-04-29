from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["MentorVerse"]
students = db["students"]

all_students = list(students.find())
student_id = '202101234'
student = students.find_one({"student_id": student_id})

@app.route("/")
def home():
    return render_template("Home-page.html")

# static pages

@app.route("/Home-page")
def home_page():
    return render_template("Home-page.html")


@app.route("/faq-page")
def faq_page():
    return render_template("faq-page.html")


@app.route("/contact-us-page")
def contact_us_page():
    return render_template("contact-us-page.html")


@app.route("/about-us-page")
def about_us_page():
    return render_template("about-us-page.html")


@app.route("/error-page")
def error_page():
    return render_template("error-page.html")


# authentication pages  
@app.route("/login-page")
def login_page():
    return render_template("login-page.html")

@app.route("/register-page")
def register_page():
    return render_template("register-page.html")

@app.route("/forgot-password-page")
def forgot_password_page():
    return render_template("forgot-password-page.html")




# student pages  

@app.route("/student-dashboard-page")
def student_dashboard_page():

    return render_template("student-dashboard-page.html", )


@app.route("/student-transcript-page")
def student_transcript_page():

    return render_template("student-transcript-page.html", )


@app.route("/student-schedule-page")
def student_schedule_page():
    
    return render_template("student-schedule-page.html", student=student)


@app.route("/student-notification-page")
def student_notification_page():

    return render_template("student-notification-page.html" )

@app.route("/student-settings-page")
def student_settings_page():

    return render_template("student-settings-page.html" )


# advisor pages
@app.route("/advisor-students-list-page")
def advisor_students_list_page():

    return render_template("advisor-students-list-page.html" )

@app.route("/advisor-student-performance-cards")
def advisor_student_performance_cards():

    return render_template("advisor-student-performance-cards.html" )


@app.route("/advisor-student-performance-page")
def advisor_student_performance_page():

    return render_template("advisor-student-performance-page.html" )


@app.route("/advisor-notification-page")
def advisor_notification_page():

    return render_template("advisor-notification-page.html" )

@app.route("/advisor-settings-page")
def adviso_settings_page():

    return render_template("advisor-settings-page.html" )



# admin page
@app.route("/admin-page")
def admin_page():

    return render_template("admin-page.html" )


if __name__ == "__main__":
    app.run(debug=True) 