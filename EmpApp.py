from flask import Flask, render_template, request, flash
from pymysql import connections
from datetime import datetime
import os
import re
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'



@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Homepage.html')


@app.route("/GetEmpRoute", methods=['GET', 'POST'])
def GetEmpRoute():
    return render_template('GetEmp.html')

@app.route("/GetEmp", methods=['GET', 'POST'])
def GetEmp():
    emp_id = (request.form['emp_id']).lower()
    check_sql = "SELECT emp_id FROM employee WHERE emp_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (emp_id))
    emp_id = re.sub('\W+','', str(cursor.fetchall()))
    check_sql = "SELECT first_name FROM employee WHERE emp_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (emp_id))
    emp_fname = re.sub('\W+','', str(cursor.fetchall()))
    check_sql = "SELECT last_name FROM employee WHERE emp_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (emp_id))
    emp_lname = re.sub('\W+','', str(cursor.fetchall()))
    check_sql = "SELECT pri_skill FROM employee WHERE emp_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (emp_id))
    emp_interest = re.sub('\W+','', str(cursor.fetchall()))
    check_sql = "SELECT location FROM employee WHERE emp_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (emp_id))
    emp_location = re.sub('\W+','', str(cursor.fetchall()))
    check_sql = "SELECT check_in FROM employee WHERE emp_id=(%s)"
    emp_image_url = "https://s3-tanyilun-bucket.s3.amazonaws.com/emp-id-" + str(emp_id) + "_image_file"
    if str(emp_fname) != "":
        return render_template('GetEmpOutput.html', id=emp_id, fname=emp_fname, 
        lname=emp_lname, interest=emp_interest, location=emp_location, image_url = emp_image_url)
    else:
        print("Invalid ID")
        return render_template('GetEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/RegisterPageRoute", methods=['POST', 'GET'])
def toRegisterPage():
    return render_template('RegisterPage.html')

@app.route("/Register", methods=['POST', 'GET'])
def registerAccount():
#to read user
    user_id = (request.form['user_id']).lower()
    user_password = request.form['user_password']
    user_confirm_password = request.form["user_confirm_password"]

    insert_sql = "INSERT INTO user VALUES (%s, %s)"
    check_sql = "SELECT * FROM user WHERE user_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (user_id))
    userid_no=cursor.fetchall()

    if user_confirm_password!=user_password:
        print("Confirm your password again")
        return render_template('RegisterPage.html')
    elif str(userid_no) != "()":
        print("User Id already exist")
        return render_template('RegisterPage.html')
    else:
        try:

            cursor.execute(insert_sql, (user_id, user_password))
            db_conn.commit()

        finally:
            cursor.close()

        print("Successfully registered, redirecting to login page")
        return render_template("LoginPage.html")
 

@app.route("/LoginUser", methods=['POST', 'GET'])
def LoginUser():
    user_id = (request.form['user_id']).lower()
    user_password = request.form['user_password']

    check_id = "SELECT * FROM user WHERE user_id=(%s)"
    check_pw = "SELECT * FROM user WHERE user_password=(%s)"
    cursor.execute(check_id, (user_id))
    id_sql = str(cursor.fetchall())
    cursor = db_conn.cursor()
    cursor.execute(check_pw, (user_password))
    pw_sql = str(cursor.fetchall())
    correct_id = False
    correct_pw = False
    cursor = db_conn.cursor()
    
    
    if id_sql !="()":
        correct_id = True

    if pw_sql !="()":
        correct_pw = True
   
    if correct_id and correct_pw:
        print("Login successful")
        return render_template('AddEmp.html')
    else:
        print("Invalid user id or/and password")
        correct_id = False
        correct_pw = False
        return render_template('LoginPage.html')


@app.route("/LoginPageRoute")
def toLoginPage():
    return render_template('LoginPage.html')

@app.route("/attendance")
def attendance():
    return render_template('AttendanceTaking.html', date=datetime.now())

@app.route("/attendanceCheckIn", methods=['POST', 'GET'])
def checkInAttendance():
    emp_id = request.form['emp_id']

    update_statement = "UPDATE employee SET check_in = (%(check_in)s) WHERE emp_id = %(emp_id)s"

    cursor = db_conn.cursor()

    LoginTime = datetime.now()
    formatted_login = LoginTime.strftime('%Y-%m-%d %H:%M:%S')
    print("Check in time:{}", formatted_login)

    try:
        cursor.execute(update_statement, {'check_in' : formatted_login, 'emp_id':int(emp_id)})
        db_conn.commit()
        print("Data updated")
    
    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("AttendanceOutput.html", date = datetime.now(),
    LoginTime = formatted_login)

@app.route("/attendance/output",methods=['GET','POST'])
def checkOut():

    emp_id = request.form['emp_id']
    select_statement = "SELECT check_in FROM employee WHERE emp_id = %(emp_id)s"
    insert_statement = "INSERT INTO attendance VALUES (%s,%s,%s)"

    cursor = db_conn.cursor()

    try:
        cursor.execute(select_statement,{'emp_id': int(emp_id)})
        LoginTime= cursor.fetchall()

        for row in LoginTime:
            formatted_login = row
            print(formatted_login[0])

        checkOutTime = datetime.now()
        LoginDate = datetime.strptime(formatted_login[0],'%Y-%m-%d %H:%M:%S' )

        formatted_checkout = checkOutTime.strpime(formatted_login[0],'%Y-%m-%d %H:%M:%S')

        try:
           cursor.execute(insert_statement,(emp_id,formatted_login[0],formatted_checkout))
           db_conn.commit()
           print("Data inserted")

        except Exception as e:
              return str(e)


    except Exception as e:
          return str(e)

    finally:
          cursor.close()

    return render_template("AttendanceOutput.html", date=datetime.now(),Checkout = formatted_checkout, 
    LoginTime= formatted_login[0])

@app.route("/addemphomepage")
def addemphome():
    return render_template('AddEmp.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']
    check_in =""

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s,%s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, check_in))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/salaryhome")
def salaryhome():
    return render_template("SalaryPage.html")


@app.route("/InsertSalary", methods=['POST', 'GET'])
def InsertSalary():
    #to read user
    user_id = (request.form['user_id']).lower()
    user_salary = request.form['user_salary']
    salary_status = "False"
    if not user_salary.isnumeric():
        print("Invalid Input Only! Please input numbers only")
        return render_template('SalaryPage.html')
 

    insert_sql = "INSERT INTO salary VALUES (%s, %s, %s)"
    check_sql = "SELECT * FROM user WHERE user_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (user_id))
    userid_no=cursor.fetchall()

   
    if str(userid_no) != "()":
        cursor.execute(insert_sql, (user_id, user_salary, salary_status))
        
    else :
        print("User does not exist")
        return render_template('SalaryPage.html')

#

    db_conn.commit()

    cursor.close()

    #print("Successfully registered, redirecting to login page")
    return render_template('GetSal.html')

@app.route("/GetSal", methods=['GET', 'POST'])
def GetSal():
    user_id = (request.form['user_id']).lower()
    insert_sql = "UPDATE salary SET salary_status = 'True' WHERE user_id = (%s)"
    check_sql = "SELECT * FROM user WHERE user_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (user_id))
    userid_no=cursor.fetchall()

   
    if str(userid_no) != "()":
        cursor.execute(insert_sql, (user_id))
        
    else :
        print("User does not exist")
        return render_template('GetSal.html')

    db_conn.commit()

    cursor.close()

    return render_template('PaidOutput.html')


@app.route("/ResetSal", methods=['GET', 'POST'])
def ResetSal():
    user_id = (request.form['user_id']).lower()
    insert_sql = "UPDATE salary SET salary_status = 'False' WHERE user_id = (%s)"
    check_sql = "SELECT * FROM user WHERE user_id=(%s)"
    cursor = db_conn.cursor()
    cursor.execute(check_sql, (user_id))
    userid_no=cursor.fetchall()

   
    if str(userid_no) != "()":
        cursor.execute(insert_sql, (user_id))
        
    else :
        print("User does not exist")
        return render_template('GetSal.html')

    db_conn.commit()

    cursor.close()

    return render_template('GetSal.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
