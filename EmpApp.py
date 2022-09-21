from flask import Flask, render_template, request
from pymysql import connections
import os
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
    return render_template('LoginPage.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/RegisterPageRoute")
def toRegisterPage:
    return render_template('RegisterPage.html')

@app.route("/Register")
def registerAccount:
    user_id = lower(request.form['user_id'])
    user_password = request.form['user_password']
    user_confirm_password = request.form["user_confirm_password"]

    insert_sql = "INSERT INTO user VALUES (%s, %s)"
    check_sql = "SELECT COUNT(user_id) FROM user WHERE user_id=(%s)"
    cursor = db_conn.cursor()

    if user_confirm_password!=user_password:
        return "Password does not match with confirm password"

    if (cursor.execute(check_sql, (user_id)))!=0
        return "User Id already exist"

    try:

        cursor.execute(insert_sql, (user_id, user_password))
        db_conn.commit()

    finally:
        cursor.close()

    print("Successfully registered, redirecting to login page")
    return render_template("LoginPage.html")

@app.route("/Login")
def registerAccount:
    user_id = lower(request.form['user_id'])
    user_password = request.form['user_password']
"
    check_id = "SELECT COUNT(user_id) FROM user WHERE user_id=(%s)"
    check_pw = "SELECT COUNT(user_password) FROM user WHERE user_password=(%s)"
    correct_id = False
    correct_pw = False
    cursor = db_conn.cursor()

    if (cursor.execute(check_id, (user_id)))>0
        correct_id = True

    if (cursor.execute(check_pw, (user_password)))>0
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
def toLoginPage:
    return render_template('LoginPage.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
