# Nutritionist Routes Blueprint

from flask import Blueprint, jsonify, request
from ..db import get_db

nutritionist_bp = Blueprint('nutritionist', __name__)

@nutritionist_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard with clients' average nutrition metrics"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
    SELECT ClientID, AVG(Quantity) AS Avg_Nutrient_Intake, Nutrient.Name,
           Nutrient.Category
    FROM MealLog
    JOIN Nutrient ON MealLog.ID = Nutrient.MealLogID
    GROUP BY ClientID, Nutrient.Name, Nutrient.Category
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    return jsonify(results)

@nutritionist_bp.route('/progress/<int:client_id>', methods=['GET'])
def get_client_progress(client_id):
    """Get progress report for a specific client"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM ProgressReport WHERE ClientID = %s"
    cursor.execute(query, (client_id,))
    results = cursor.fetchall()
    return jsonify(results)

@nutritionist_bp.route('/trends', methods=['GET'])
def get_dietary_trends():
    """Analyze dietary habits over time"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
    SELECT ClientID, DATE(Datetime) AS LogDate, Nutrient.Name, SUM(Quantity) AS Total_Intake
    FROM MealLog
    JOIN Nutrient ON MealLog.ID = Nutrient.MealLogID
    WHERE Datetime BETWEEN %s AND %s
    GROUP BY ClientID, LogDate, Nutrient.Name
    ORDER BY LogDate
    """
    
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()
    return jsonify(results)

@nutritionist_bp.route('/deficiencies', methods=['GET'])
def get_nutrient_deficiencies():
    """Identify nutrient deficiencies"""
    threshold = request.args.get('threshold', type=float)
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
    SELECT ClientID, Nutrient.Name, AVG(Quantity) AS Avg_Intake
    FROM MealLog
    JOIN Nutrient ON MealLog.ID = Nutrient.MealLogID
    GROUP BY ClientID, Nutrient.Name
    HAVING AVG(Quantity) < %s
    """
    
    cursor.execute(query, (threshold,))
    results = cursor.fetchall()
    return jsonify(results)

@nutritionist_bp.route('/clients', methods=['POST'])
def add_client():
    """Add new client and their nutrition plan"""
    data = request.get_json()
    
    db = get_db()
    cursor = db.cursor()
    
    # Add new client
    client_query = "INSERT INTO Client (Name, DOB, Email) VALUES (%s, %s, %s)"
    cursor.execute(client_query, (data['name'], data['dob'], data['email']))
    client_id = cursor.lastrowid
    
    # Add nutrition plan
    plan_query = """
    INSERT INTO NutritionPlan (StartDate, EndDate, CaloriesGoal, NutritionistID, ClientID)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(plan_query, (
        data['start_date'],
        data['end_date'],
        data['calories_goal'],
        data['nutritionist_id'],
        client_id
    ))
    
    db.commit()
    return jsonify({"message": "Client and nutrition plan added successfully", "client_id": client_id}), 201

@nutritionist_bp.route('/clients/<int:client_id>', methods=['DELETE'])
def remove_client(client_id):
    """Remove or archive inactive client"""
    db = get_db()
    cursor = db.cursor()
    
    query = "DELETE FROM Client WHERE ID = %s"
    cursor.execute(query, (client_id,))
    db.commit()
    
    return jsonify({"message": "Client removed successfully"}), 200 