from flask import Flask, request
from sqlalchemy.sql import text
from flask_cors import CORS
from db import db
from datetime import datetime


# initialize flask app
app = Flask(__name__)
CORS(app)


# DATABASE CONFIGURATION
username = 'root'
password = '1234'
server = '127.0.0.1'
dbname = '/ecommerce'

userpass = 'mysql+pymysql://' + username + ':' + password + '@'

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + server + dbname
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


# =========================
# DISPLAY PRODUCTS API
# =========================
@app.route('/api/display-products')
def displayAllProducts():

    sql = text("""
        SELECT * FROM products WHERE status = 1
    """)

    with db.engine.connect() as conn:
        response = conn.execute(sql)
        finalResponseData = response.mappings().all()

    return [dict(row) for row in finalResponseData]


# =========================
# CONTACT FORM API
# =========================
@app.route('/api/add-contact-data', methods=['POST'])
def addContactData():

    fullName = request.form.get('fullname', '')
    email = request.form.get('email', '')
    mobile = request.form.get('mobile', '')
    message = request.form.get('message', '')

    if fullName == '' or email == '' or mobile == '':
        return {'errFlag': 1, 'message': 'Full Name / Email / Mobile Missing'}

    try:

        data = {
            'full_name': fullName,
            'email': email,
            'mobile': mobile,
            'message': message,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'created_time': datetime.now().strftime('%H:%M:%S'),
            'status': 1
        }

        sql = text("""
            INSERT INTO contact_form 
            (full_name,email,mobile,message,created_date,created_time,status)
            VALUES
            (:full_name,:email,:mobile,:message,:created_date,:created_time,:status)
        """)

        with db.engine.connect() as conn:
            result = conn.execute(sql, data)
            conn.commit()

        if result.lastrowid > 0:
            return {"errFlag":0,"message":"Contact Data Saved Successfully"}
        else:
            return {"errFlag":1,"message":"Contact Data Not Saved"}

    except Exception as e:
        return {"error": str(e)}


# =========================
# BANNER CLICK TRACKING
# =========================
@app.route('/api/banner-clicks-track')
def trackBannerClicks():

    data = {
        'tdate': datetime.now().strftime('%Y-%m-%d')
    }

    sql = text("""
        SELECT COUNT(*) AS row_count,banner_clicks,id
        FROM banner_clicks
        WHERE date = :tdate
    """)

    with db.engine.connect() as conn:
        response = conn.execute(sql,data)

    finalResponseData = response.mappings().all()
    rowCount = finalResponseData[0].row_count


    if rowCount > 0:

        bannerClick = finalResponseData[0].banner_clicks
        bannerTableId = finalResponseData[0].id

        bannerData = {
            "newBannerClicks": bannerClick + 1,
            "bannerTableId": bannerTableId
        }

        sql = text("""
            UPDATE banner_clicks
            SET banner_clicks = :newBannerClicks
            WHERE id = :bannerTableId
        """)

        with db.engine.connect() as conn:
            conn.execute(sql,bannerData)
            conn.commit()


    if rowCount == 0:

        bannerDataInsert = {
            'tdate': datetime.now().strftime('%Y-%m-%d'),
            'banner_clicks': 1
        }

        sql = text("""
            INSERT INTO banner_clicks (banner_clicks,date)
            VALUES (:banner_clicks,:tdate)
        """)

        with db.engine.connect() as conn:
            conn.execute(sql,bannerDataInsert)
            conn.commit()

    return {"errFlag":0,"message":"Click Logged Successfully"}


# =========================
# APPLE LOGIN API
# =========================
@app.route('/api/apple-login', methods=['POST'])
def appleLogin():

    apple_id = request.form.get('apple_id')
    password = request.form.get('password')

    sql = text("""
        SELECT * FROM newuser
        WHERE apple_id = :apple_id AND password = :password
    """)

    data = {
        "apple_id": apple_id,
        "password": password
    }

    with db.engine.connect() as conn:
        result = conn.execute(sql,data)
        user = result.mappings().first()

    if user:
        return {"status":1,"message":"Login successful"}
    else:
        return {"status":0,"message":"Invalid Apple ID or password"}


# =========================
# REGISTER USER API
# =========================
@app.route('/api/register-user', methods=['POST'])
def registerUser():

    data = request.get_json()

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    country = data.get("country")
    dob = data.get("dob")
    apple_id = data.get("apple_id")
    password = data.get("password")
    phone = data.get("phone")

    sql = text("""
        INSERT INTO newuser
        (first_name,last_name,country,dob,apple_id,password,phone,created_date)
        VALUES 
        (:first_name,:last_name,:country,:dob,:apple_id,:password,:phone,:created_date)
    """)

    insertData = {
        "first_name": first_name,
        "last_name": last_name,
        "country": country,
        "dob": dob,
        "apple_id": apple_id,
        "password": password,
        "phone": phone,
        "created_date": datetime.now().strftime('%Y-%m-%d')
    }

    with db.engine.connect() as conn:
        conn.execute(sql, insertData)
        conn.commit()

    return {"status":1,"message": "Apple ID created successfully"}


# =========================
# RUN SERVER
# =========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)