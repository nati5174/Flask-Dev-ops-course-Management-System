from flask import Flask, request, render_template, redirect, url_for, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql.expression import false
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(300),nullable=False)
    type = db.Column(db.String(20), nullable=False)
    #notes = db.relationship('Marks', backref='author', lazy = True)

   # def __repr__(self):
       # return f"Person({self.username}, {self.email})"


class Marks(db.Model):
    assignment_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=False, nullable=False)
    #type = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    student_username = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return f"Marks({self.student_username}, {self.grade})"

class Remark(db.Model):
    remark_id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(30), nullable = False)
    title = db.Column(db.String(30), unique=False, nullable=False)
    remark_msg = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(10), default= "No Remark Request Sent", nullable=False)

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    mess1 = db.Column(db.String(500), nullable=False)
    mess2 = db.Column(db.String(500), nullable=False)
    mess3 = db.Column(db.String(500), nullable=False)
    mess4 = db.Column(db.String(500), nullable=False)
    instructor_username = db.Column(db.String(30), unique=False, nullable = False)
    status = db.Column(db.String(20), default= "Opened", nullable=False)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'name' in session:
        return render_template('index.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/assign', methods=['GET', 'POST'])
def assign():
    if 'name' in session:
        return render_template('assign.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))


@app.route('/new', methods=['GET'])
def new():
    if 'name' in session:
        return render_template('new.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/calendar', methods=['GET'])
def calendar():
    if 'name' in session:
        return render_template('calendar.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/lec', methods=['GET'])
def lec():
    if 'name' in session:
        return render_template('lec.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/labs', methods=['GET'])
def labs():
    if 'name' in session:
        return render_template('labs.html')

    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/tests', methods=['GET'])
def tests():
    if 'name' in session:
        return render_template('tests.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))


@app.route('/res', methods=['GET'])
def res():
    if 'name' in session:
        return render_template('res.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route('/syl',methods=['GET'])
def syl():
    if 'name' in session:
        return render_template('syl.html')
    else:
        flash("You Must be logged in, to access this..")
        return redirect(url_for('login'))

@app.route("/", methods=['GET', 'POST'])
def register():
        
        if request.method == 'GET':
            return render_template('register.html')
        else:
            registar_data = request.form
            username = registar_data["username_reg"]
            email = registar_data["email_reg"]
            password = registar_data["pswd_reg"]
            if password == "":
                flash("Password must non be empty")
                return render_template('register.html')
            
            if  username =='' or email == '':
                flash("Username or Email must be filled")
                return render_template('register.html')

            type = registar_data["type"]
           
            
            hashed_password = bcrypt.generate_password_hash(password=password).decode('utf-8')

            if Person.query.filter_by(username=username).first() or Person.query.filter_by(email=email).first():
                flash("User already with this username or email")
                return render_template('register.html')

            else:
                reg_data = (username, email, hashed_password, type)
                add_user(reg_data)
                return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':

        if 'name' in session:
            flash("Already Logged in")
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    
    else:
        login_data = request.form
        username = login_data["username_log"]
        password = login_data["pswd_log"]

        person = Person.query.filter_by(username=username).first()

        if not person or not bcrypt.check_password_hash(person.password, password):
            flash("Please check your login details again and make sure you have an account", "error")
            return render_template('login.html')
       
        else:

            session['name'] = username
            session['type'] = person.type
            if person.type == 'Student':
                session['instructors'] = query_all_instructor()
                marks = query_all_marks_student(username)

                session['assignments'] = [mark.title for mark in marks]
                
            else:
                session['students'] = query_all_student()
                session['title_assignments']  = ["Assignment1", "Assignment2", "Assignment3", "Lab1", "Lab2", "Lab3", "Lab4", "Lab5", "Lab6", "Lab7", "Lab8", "Lab9", "Midterm", "Final Exam"]
   
            session.permanent= True
            return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('name', default=None)
    session.pop('type', default=None)
    session.pop('instructors', default=None)
    session.pop('students', default=None)
    session.pop('typeofassignments', default=None)


    return redirect(url_for('login'))



@app.route('/enter_grade', methods=['GET', 'POST'])
def enter_grade():
    
    if request.method == 'GET':
        if 'name' in session and session['type'] == "Instructor":
                return render_template('enter_grade.html')
        else:
            flash("You don't have access to that page..")
            return redirect(url_for('logout'))
    else:
        data = request.form
         
        student = data['student']
        title = data['title']

        if student == "Select Student":
            flash("Select another student please")
            return render_template('enter_grade.html')
        elif title == "Select Assignment":
            flash("Select another title")
            return render_template('enter_grade.html')
        else:
        
            grade = data['grade']
            
            person = Person.query.filter_by(username=student).first()
            person2 = Marks.query.filter_by(student_username=student).filter_by(title=title).first()

            if not person:
                flash("Student does not exist", "error")
                return render_template('enter_grade.html')
            elif grade == "":
                flash("Enter Grade")
                return render_template('enter_grade.html')

            elif person2:
                flash("Student already has a mark for this assignment", "error")
                return render_template('enter_grade.html')


            else:
                mark_data = (title, grade, student)
                add_mark(mark_data)
                flash('"Marks updated successfully!"')
                return render_template('enter_grade.html')
       
@app.route('/view_grades', methods=['GET'])
def view_grades():
        
    if request.method == 'GET':
        if 'name' in session and session['type'] == "Instructor":
            all_marks = query_all_marks()
            return render_template("view_grades.html", all_marks = all_marks)
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout'))   
        

@app.route('/view_grades_student', methods=['GET'])
def view_grades_student():

    if request.method == 'GET':
        if 'name' in session and session['type'] == "Student":
            if session['type'] == 'Student':
                username = session['name']

                all_marks = query_all_marks_student(username)
                get_data = get_status(all_marks)

                new_data = []
                for i in range(len(all_marks)):
                    new_data.append((all_marks[i],get_data[i]))

                return render_template("view_grades_student.html", new_data = new_data)
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout'))   

        

@app.route('/remark', methods=['GET', 'POST'])    
def remark():

    if request.method == 'GET':
        if 'name' in session and session['type'] == "Student":
            return render_template('remark.html') 
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout'))   
    
    else:
        data =request.form
        student_name = session['name']
        assignment = data['assignment']
        if assignment == "Assessment":
            flash("You have to pick an actual a assessment")
            return render_template("remark.html")
        
        reason = data['reason']

        already_remark = Remark.query.filter_by(student_username=student_name).filter_by(title=assignment).first()
        if already_remark:
            flash("You have already requested a remark for this assignment")
            return render_template("remark.html")  

        else:
            remark_info = (student_name,assignment,reason)
            add_remark(remark_info)
            flash("Remark request submitted successfully")
            return render_template("remark.html")  


@app.route('/remark_req', methods=['GET', 'POST'])
def remark_req():

    if request.method=="GET":
        if 'name' in session and session['type'] == "Instructor":
            all_remarks = query_remarks()
            i = [marks for  marks in all_remarks]
            return render_template('remark_req.html', all_remarks=all_remarks)
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout')) 

    else:
        data = request.form
        remark = data['stdnt_reason']
        if remark == 'View Remark Requests':
            flash("You have to pick a remark request")
            return redirect(url_for('remark_req'))
       
       
       

        else:
            print(remark)
            result = data['remark_desc']
            new_grade = data['new_mark']
            remark = remark.split('|')
            student = remark[0]
            student= student[8:]
            title = remark[1]
            title = title[6:]

            if result == "Decline":
                remark = Remark.query.filter_by(student_username=student).filter_by(title=title).first()
                remark.status = "Rejected"
                db.session.commit()
                return redirect(url_for('remark_req'))

            elif result == "Accept":
                if new_grade == "":
                    flash("You need to select a new grade")
                    return redirect(url_for('remark_req'))

                else:
                    remark = Remark.query.filter_by(student_username=student).filter_by(title=title).first()
                    remark.status = "Approved"
                    mark = Marks.query.filter_by(student_username=student).filter_by(title=title).first()
                    mark.grade = new_grade
                    db.session.commit()
                    flash("Mark Updated")

                    return redirect(url_for('remark_req'))

@app.route('/student_feedback', methods=['GET', 'POST'])
def student_feedback():
    
    if request.method == 'GET':
        if "name" in session and  session['type'] == "Student":
            return render_template('student_feedback.html')
        
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout')) 

    
    else:
        data = request.form
        instructor = data['instructor']
        mess1 = data['mess1']
        mess2 = data['mess2']
        mess3 = data['mess3']
        mess4 = data['mess4']

        if (mess1 and mess2 and mess2 and mess4) == '':
            flash('Fill out all sections', "error")
            return render_template('student_feedback.html')

        else:
            feedback_details = (mess1,mess2, mess3, mess4, instructor)
            add_feedback( feedback_details)
            
            flash('"Feedback Sent!"')
            return render_template('student_feedback.html')


@app.route('/anon_mail', methods=['GET', 'POST'])
def anon_mail():

    if request.method == 'GET':
        if "name" in session and session['type'] == "Instructor":

            all_feedback = query_feedback()
            opened_feedback = all_feedback[0]
            opened_feedback = [f"1.{feed.mess1},2.{feed.mess2},3.{feed.mess2},4.{feed.mess4}" for feed in opened_feedback]

            return render_template('anon_mail.html', opened_feedback=opened_feedback)
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout')) 

    else:
        data = request.form
        feedback  = data['feedback']

        if feedback == "View Students Feedback":
            flash("You cannot submit without any feeback")
            return redirect(url_for('anon_mail'))

        
        feedback = feedback.split(',')
        
        feedback = [msg[2:] for msg in feedback]

        mess12 = feedback[0]
        mess22 = feedback[1]

        mess32 = feedback[2]
        mess42 = feedback[3]


        feedback = Feedback.query.filter_by(mess1=mess12).filter_by(mess2=mess22).filter_by(mess3=mess32).filter_by(mess4=mess42).first()
        print("____this is before the error______")

        feedback.status = "Reviewed"
        db.session.commit()
        flash("Submited")

        return redirect(url_for('anon_mail'))
    

@app.route('/view_anon', methods=['GET'])
def view_anon():
        
        if "name" in session and session['type'] == "Instructor":
            all_feedback = query_feedback()
            opened_feedback = all_feedback[0]
            reviewed_feedback = all_feedback[1]

            return render_template('view_anon.html',opened_feedback=opened_feedback, reviewed_feedback=reviewed_feedback)
        else:
            flash("You do not have permission to access this..")
            return redirect(url_for('logout')) 
        
def add_user(reg_details):
    
        student = Person(username=reg_details[0],email=reg_details[1], password=reg_details[2], type=reg_details[3])
        db.session.add(student)
        db.session.commit()    

def add_mark(mark_details):
   
    mark = Marks(title=mark_details[0], grade=mark_details[1], student_username=mark_details[2])
    #if session['assignments'] != None:
        #session['assignments'].append(mark.title)
    db.session.add(mark)
    db.session.commit()

def add_feedback(feedback_details):
   
    feedback = Feedback(mess1=feedback_details[0], mess2=feedback_details[1], mess3=feedback_details[2], mess4=feedback_details[3],instructor_username=feedback_details[4])
    db.session.add(feedback)
    db.session.commit()          

def get_status(marks):

    idk = []
    for mark in marks:
        remark = Remark.query.filter_by(student_username = mark.student_username).filter_by(title=mark.title).first()
        if remark:
            idk.append(remark.status)
        else:
            idk.append("No Remark Requested")

    return idk        

def add_remark(remark_details):
    remark = Remark(student_username=remark_details[0], title=remark_details[1], remark_msg=remark_details[2], status= "Pending")
    db.session.add(remark)
    db.session.commit()          


def query_all_marks():
    all_marks = Marks.query.all()
    return all_marks



def query_feedback():
  
    opened_feedback = Feedback.query.filter_by(instructor_username=session['name']).filter_by(status="Opened").all()
    reviewed_feedback = Feedback.query.filter_by(instructor_username=session['name']).filter_by(status="Reviewed").all()

    return (opened_feedback, reviewed_feedback)


def query_remarks():
    all_remarks = Remark.query.filter_by(status="Pending")
    all_remarks = [f"Student:{remarks.student_username}|Title:{remarks.title}|Reason:{ remarks.remark_msg}" for remarks in all_remarks]
    return all_remarks


def query_all_marks_student(username):
    all_marks = Marks.query.filter_by(student_username=username).all()

    return all_marks



def query_all_instructor():
    instructors = Person.query.filter_by(type='Instructor').all()
    usernames = [instructor.username for instructor in instructors]
    return usernames


def query_all_student():
    students = Person.query.filter_by(type='Student').all()
    usernames = [student.username for student in students]
    return usernames


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        hashed_password1 = bcrypt.generate_password_hash(password='password123').decode('utf-8')
        hashed_password2 = bcrypt.generate_password_hash(password='password123').decode('utf-8')

        person1 = Person(username='Purva', email='purva@example.com', password=hashed_password1, type='Instructor')
        person2 = Person(username='Jane_doe', email='jane@example.com', password=hashed_password2, type='Student')
        grade1 = Marks(title='Assignment1', grade=74, student_username='Jane_doe')
        remark2 = Remark(student_username="Jane_doe", title='Assignment1', remark_msg = "IDK", status="Pending")
        if not Person.query.first():
            db.session.add_all([person1, person2, grade1, remark2])
            db.session.commit()
        db.session.close()
    app.run(host='0.0.0.0', port=5000, debug=True)
