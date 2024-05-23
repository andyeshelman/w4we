from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

from config import DATABASE, USER, PASSWORD, HOST

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
        )

        if conn.is_connected():
            return conn
        
    except Error as e:
        print("Error: {e}")
        return None

app = Flask(__name__)
app.json.sort_keys = False
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String()
    phone = fields.String()
    credit_card = fields.String()

    class Meta:
        fields = "id", "name", "email", "phone", "credit_card"

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSchema(ma.Schema):
    activity = fields.String(required=True)
    member_id = fields.Int(required=True)
    date = fields.Date()

    class Meta:
        fields = "id", "member_id", "activity", "date"

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

@app.route('/')
def home():
    return "Let's gooooooooooooooooooooo"


@app.route("/members", methods=["GET"])
def get_members():
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM Members")
            members = cursor.fetchall()
            return members_schema.jsonify(members)   
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            keys = ", ".join(member_data.keys())
            values = ", ".join(repr(v) for v in member_data.values())
            query = f"INSERT INTO Members({keys}) VALUES ({values})"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "New member was added successfully"}), 201  
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            fields = (key + " = " + repr(value) for key, value in member_data.items())
            query = f"UPDATE Members SET {", ".join(fields)} WHERE id = {id}"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "Member details updated successfully"}), 200
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            query = f"SELECT * FROM Members WHERE id = {id}"
            cursor.execute(query)
            if not cursor.fetchall():
                return jsonify({"message": "Member not found"}), 404
            query = f"SELECT * FROM Workouts WHERE member_id = {id}"
            cursor.execute(query)
            if cursor.fetchall():
                return jsonify({"message": "Member has recorded workouts, cannot delete"}), 400
            query = f"DELETE FROM Members WHERE id = {id}"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "Member removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/workouts", methods=["GET"])
def get_workouts():
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM Workouts")
            workouts = cursor.fetchall()
            return workouts_schema.jsonify(workouts)   
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500


@app.route("/workouts", methods=["POST"])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            if "date" in workout_data:
                workout_data["date"] = str(workout_data["date"])
            keys = ", ".join(workout_data.keys())
            values = ", ".join(repr(v) for v in workout_data.values())
            query = f"INSERT INTO Workouts({keys}) VALUES ({values})"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "New workout was added successfully"}), 201  
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

@app.route("/workouts/<int:id>", methods=["PUT"])
def update_workout(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            if "date" in workout_data:
                workout_data["date"] = str(workout_data["date"])
            fields = (key + " = " + repr(value) for key, value in workout_data.items())
            query = f"UPDATE Workouts SET {", ".join(fields)} WHERE id = {id}"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "Workout details updated successfully"}), 200
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            query = f"SELECT * FROM Workouts WHERE id = {id}"
            cursor.execute(query)
            if not cursor.fetchall():
                return jsonify({"message": "Workout not found"}), 404
            query = f"DELETE FROM Workouts WHERE id = {id}"
            cursor.execute(query)
            conn.commit()
            return jsonify({"message": "Workout removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/workoutsbymember/<int:id>", methods=["GET"])
def get_workouts_by_member(id):
    try:
        with get_db_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM Workouts WHERE member_id = {id}")
            workouts = cursor.fetchall()
            return workouts_schema.jsonify(workouts)   
    except Error as e:
        print(f"ERROR: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True)