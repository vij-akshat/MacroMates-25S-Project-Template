from flask import Blueprint, jsonify, request
from ..db import get_db_connection

nutritionist_bp = Blueprint('nutritionist', __name__)

@nutritionist_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get nutritionist dashboard data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total clients
        cursor.execute("SELECT COUNT(*) as total_clients FROM clients")
        total_clients = cursor.fetchone()['total_clients']
        
        # Get recent progress updates
        cursor.execute("""
            SELECT c.client_name, p.progress_date, p.weight, p.body_fat_percentage
            FROM progress p
            JOIN clients c ON p.client_id = c.client_id
            ORDER BY p.progress_date DESC
            LIMIT 5
        """)
        recent_progress = cursor.fetchall()
        
        # Get meal plan statistics
        cursor.execute("""
            SELECT COUNT(*) as total_plans,
                   AVG(calories) as avg_calories,
                   AVG(protein) as avg_protein,
                   AVG(carbs) as avg_carbs,
                   AVG(fats) as avg_fats
            FROM meal_plans
        """)
        meal_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_clients': total_clients,
            'recent_progress': recent_progress,
            'meal_statistics': meal_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutritionist_bp.route('/clients', methods=['GET'])
def get_clients():
    """Get all clients with their basic information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT client_id, client_name, email, join_date, 
                   current_weight, target_weight, activity_level
            FROM clients
            ORDER BY client_name
        """)
        clients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(clients)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutritionist_bp.route('/progress/<int:client_id>', methods=['GET'])
def get_client_progress(client_id):
    """Get progress history for a specific client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT progress_date, weight, body_fat_percentage, 
                   muscle_mass, water_percentage, notes
            FROM progress
            WHERE client_id = %s
            ORDER BY progress_date DESC
        """, (client_id,))
        
        progress = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(progress)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutritionist_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get nutritional trends across all clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get average nutrient intake trends
        cursor.execute("""
            SELECT DATE(meal_date) as date,
                   AVG(calories) as avg_calories,
                   AVG(protein) as avg_protein,
                   AVG(carbs) as avg_carbs,
                   AVG(fats) as avg_fats
            FROM meal_logs
            GROUP BY DATE(meal_date)
            ORDER BY date DESC
            LIMIT 30
        """)
        trends = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(trends)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutritionist_bp.route('/deficiencies', methods=['GET'])
def get_nutrient_deficiencies():
    """Get common nutrient deficiencies across clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT nutrient_name, COUNT(*) as deficiency_count
            FROM nutrient_deficiencies
            GROUP BY nutrient_name
            ORDER BY deficiency_count DESC
        """)
        deficiencies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(deficiencies)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 