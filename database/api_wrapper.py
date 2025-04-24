import json
from flask import Flask, request, jsonify
from database.manager_db import DatabaseManager

class CrosswordAPI:
    """API wrapper for the crossword database manager"""
    
    def __init__(self, db_manager=None):
        """Initialize the API wrapper"""
        self.db = db_manager if db_manager else DatabaseManager()
        
    def configure_routes(self, app):
        """Configure Flask routes"""
        
        # User endpoints
        @app.route('/api/login', methods=['POST'])
        def login():
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({"status": "error", "message": "Username and password required"}), 400
                
            user = self.db.authenticate_user(username, password)
            if user:
                return jsonify({
                    "status": "ok", 
                    "message": "Login successful",
                    "user_id": user['id'],
                    "username": user['username']
                })
            else:
                return jsonify({"status": "error", "message": "Invalid username or password"}), 401
        
        @app.route('/api/register', methods=['POST'])
        def register():
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({"status": "error", "message": "Username and password required"}), 400
                
            result = self.db.register_user(username, password)
            if result:
                return jsonify({
                    "status": "ok", 
                    "message": "Registration successful",
                    "user_id": result['user_id'],
                    "username": result['username']
                })
            else:
                return jsonify({"status": "error", "message": "Username already exists"}), 409
        
        @app.route('/api/users/<int:user_id>/stats', methods=['GET'])
        def get_user_stats(user_id):
            stats = self.db.get_user_stats(user_id)
            if stats:
                return jsonify({"status": "ok", "stats": stats})
            else:
                return jsonify({"status": "error", "message": "User not found"}), 404
        
        # Puzzle endpoints
        @app.route('/api/puzzles', methods=['GET'])
        def get_puzzles():
            puzzles = self.db.get_all_puzzles()
            return jsonify({"status": "ok", "puzzles": puzzles})
        
        @app.route('/api/puzzles/<int:puzzle_id>', methods=['GET'])
        def get_puzzle(puzzle_id):
            puzzle = self.db.get_puzzle_detail(puzzle_id)
            if puzzle:
                return jsonify({"status": "ok", "puzzle": puzzle})
            else:
                return jsonify({"status": "error", "message": "Puzzle not found"}), 404
        
        @app.route('/api/puzzles', methods=['POST'])
        def create_puzzle():
            data = request.json
            # Validate required fields
            required_fields = ['name', 'gridSize', 'visibleSquares', 'words', 'clues', 
                              'lateralWords', 'verticalWords', 'creator_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
            
            result = self.db.create_puzzle(data)
            if result['status'] == 'ok':
                return jsonify({
                    "status": "ok", 
                    "message": "Puzzle created successfully",
                    "puzzle_id": result['puzzle_id']
                })
            else:
                return jsonify({"status": "error", "message": result.get('message', 'Failed to create puzzle')}), 400
        
        # Solution endpoints
        @app.route('/api/puzzles/<int:puzzle_id>/solve/start', methods=['POST'])
        def start_attempt(puzzle_id):
            data = request.json
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({"status": "error", "message": "User ID required"}), 400
                
            attempt_id = self.db.start_puzzle_attempt(user_id, puzzle_id)
            return jsonify({
                "status": "ok", 
                "message": "Attempt started",
                "attempt_id": attempt_id
            })
        
        @app.route('/api/attempts/<int:attempt_id>/progress', methods=['POST'])
        def update_progress(attempt_id):
            data = request.json
            progress = data.get('progress')
            
            if not progress:
                return jsonify({"status": "error", "message": "Progress data required"}), 400
                
            self.db.update_puzzle_progress(attempt_id, progress)
            return jsonify({"status": "ok", "message": "Progress updated"})
        
        @app.route('/api/attempts/<int:attempt_id>/complete', methods=['POST'])
        def complete_attempt(attempt_id):
            data = request.json
            successful = data.get('successful', False)
            
            result = self.db.complete_puzzle_attempt(attempt_id, successful)
            if result:
                return jsonify({
                    "status": "ok", 
                    "message": "Attempt completed",
                    "duration": result['duration'],
                    "successful": result['successful']
                })
            else:
                return jsonify({"status": "error", "message": "Attempt not found"}), 404
        
        @app.route('/api/solutions', methods=['POST'])
        def submit_solution():
            data = request.json
            user_id = data.get('user_id')
            puzzle_id = data.get('puzzle_id')
            solution = data.get('solution')
            
            if not all([user_id, puzzle_id, solution]):
                return jsonify({"status": "error", "message": "Missing required fields"}), 400
                
            result = self.db.submit_solution(user_id, puzzle_id, solution)
            return jsonify(result)
        
        # Leaderboard endpoints
        @app.route('/api/leaderboards', methods=['GET'])
        def get_leaderboards():
            leaderboards = self.db.get_leaderboards()
            return jsonify({"status": "ok", "leaderboards": leaderboards})
        
        @app.route('/api/puzzles/<int:puzzle_id>/leaderboard', methods=['GET'])
        def get_puzzle_leaderboard(puzzle_id):
            leaderboard = self.db.get_puzzle_leaderboard(puzzle_id)
            return jsonify({"status": "ok", "leaderboard": leaderboard})
        
        # Rating endpoints
        @app.route('/api/puzzles/<int:puzzle_id>/ratings', methods=['GET'])
        def get_ratings(puzzle_id):
            ratings = self.db.get_puzzle_ratings(puzzle_id)
            if ratings:
                return jsonify({"status": "ok", "ratings": ratings})
            else:
                return jsonify({"status": "error", "message": "Failed to get ratings"}), 500
        
        @app.route('/api/puzzles/<int:puzzle_id>/rate', methods=['POST'])
        def rate_puzzle(puzzle_id):
            data = request.json
            user_id = data.get('user_id')
            rating = data.get('rating')
            comment = data.get('comment')
            
            if not user_id or not rating:
                return jsonify({"status": "error", "message": "User ID and rating required"}), 400
                
            result = self.db.rate_puzzle(user_id, puzzle_id, rating, comment)
            if result['status'] == 'ok':
                return jsonify({"status": "ok", "message": "Rating submitted"})
            else:
                return jsonify({"status": "error", "message": result.get('message', 'Failed to submit rating')}), 500
                
        return app

def create_api(app=None):
    """Create a Flask app with API routes configured"""
    if app is None:
        app = Flask(__name__)
    
    api = CrosswordAPI()
    return api.configure_routes(app)

if __name__ == "__main__":
    app = create_api()
    app.run(debug=True, port=5000) 
