from flask import Flask, request, jsonify
from random import randrange
import psycopg2
import crypt
import json
import jwt
from twilio.rest import Client
import os


app = Flask(__name__)

conn_string = os.getenv('db_endpoint')
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
account_sid = os.getenv('twilio_sid') #  Both found on twilio user dashboard
auth_token = os.getenv('twilio_token')# 
client = Client(account_sid, auth_token)




# Sample function which registers user via POST REQUEST
@app.route('/sample_register', methods =['POST'])
def register_user():
    data = request.get_json()

    if(get_user(data['phone_number']) != []):
        return jsonify({"msg": "User Exists"}), 409

    else:
            
        try:
            data = request.get_json()

            hashed_password = crypt.crypt(data['plaintext_pass'], crypt.METHOD_SHA256)

            sql_statement = "INSERT INTO new_project.user_base(first_name, surname, phone_number, password_hash) values({},{},{},{});"
            executed_statement = sql_statement.format(data['first_name'], data['surname'], data['phone_number'], "\'" + hashed_password + "\'")
            cursor.execute(executed_statement)

            code = get_code()
            sql_statement = "INSERT INTO new_project.confirmation(phone_number, code) values({},{});".format(data['phone_number'], code)
            
            cursor.execute(sql_statement)
            conn.commit()

            try:
                send_confirmation_code(code, data['phone_number'])
                return jsonify({"msg": "Success"}), 200
            except Exception as err:
                 return jsonify({"msg": "<YOUR ERROR MESSAGE>"}), 401
            
        except Exception as e:
            conn.rollback()
            return jsonify({"msg": str(e)})




# Sample function which runs after user POSTs their confirmation code
@app.route('/sample_confirm_user', methods=['POST'])
def confirm_user():

    number = request.get_json()['phone_number']
    code = request.get_json()['confirm_code']
    uid = request.get_json()['user_id']
    fetched_numb = get_confirmation_row(number, uid)
     
    if (fetched_numb[0] == number and fetched_numb[1] == code ):
        return jsonify({"msg": "DESIRED SUCCESS MESSAGE"}), 200

    else:
        return jsonify({"msg": "DESIRED ERROR MESSAGE"}), 401


# Helper function that confirms a user's account after submitting their confirmation code
def confirm_user(user_id):
    try:
        sql_statement = "UPDATE {}.{} SET confirmed_account = 1 where uid = {};".format("YOUR SCHEMA", "YOUR USER TABLE", user_id)
        cursor.execute(sql_statement)
        conn.commit()
    except Exception as error:
        conn.rollback()
        return {"ERROR": "YOUR ERROR MESSAGE"}


# Helper function to fetch row with phone number and assigned confirmation code
def get_confirmation_row(phone_number, user_id):
    try:
        sql_command = "SELECT a.* FROM new_project.confirmation_keys a, new_project.user_base b where a.phone_number = \'{}\'  and a.phone_number = b.phone_number and b.uid =  \'{}\' ".format(phone_number, user_id)
        data = cursor.execute(sql_command)
        rv = cursor.fetchall()

        return list(rv[0])
        
    except Exception as e:
            
        if(str(e) == 'list index out of range'):
                
            return []
            
        else:
            return {'msg': e}


# Twilio function which sends out SMS with confirmation code
def send_confirmation_code(code, number):

    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body="Your confirmation code is {} ".format(code),
                     from_='YOUR TWILIO PHONE NUMBER',
                     to='+1'+number
                 )

# Helper function which fetches user based on their phone number
def get_user(phone_number):
    
    try:
        sql_command = "SELECT * FROM {}.{} where phone_number = \'{}\'".format("YOUR SCHEMA", "YOUR USER TABLE", phone_number)
        print(sql_command)
        data = cursor.execute(sql_command)
        rv = cursor.fetchall()

        return list(rv[0])
    
    except Exception as e:
        
        if(str(e) == 'list index out of range'):
            
            return []
        
        else:
            return {'msg': e}


# Helper function to get 5 digit confirmation code
def get_code():

    return randrange(10000, 99999, 1)




if __name__ == '__main__':
    app.run()
