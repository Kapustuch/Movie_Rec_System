import os
import sqlite3
from flask import Flask, render_template, request, jsonify
# Import database utility functions
from database import save_group_to_queue, get_current_queue, init_db
# Import the AI recommendation generation function
from ai_advisor import get_movie_recommendation

# Initialize the Flask application instance
app = Flask(__name__)

# Static list of movies to be displayed in the web interface
MOVIES_LIST = ["Інтерстеллар", "Той що біжить лабіринтом", "Пірати Карибського моря", "Дюна", "Початок"]

@app.route('/')
def index():
    """Renders the main page containing the delivery configuration form."""
    # Pass the movie list to the index.html template for checkboxes rendering
    return render_template('index.html', movies=MOVIES_LIST)

@app.route('/generate', methods=['POST'])
def generate():
    """Processes the macro targeting choices and generates package structures for the AI."""
    # Read chosen data arrays from the submitted HTML form
    selected_movies = request.form.getlist('movies')
    chosen_strategies = request.form.getlist('strategies')
    
    # NEW logic: strictly empty string if strategy is not checked
    target_ages = [""]
    target_interests = [""]
    
    # If 'age_group' macro is checked, expand list to target all 3 age groups
    if "age_group" in chosen_strategies:
        target_ages = ["teen", "adult", "senior"]
        
    # If 'interest' macro is checked, expand list to target all 3 interest categories
    if "interest" in chosen_strategies:
        target_interests = ["action", "drama", "general"]

    # Nested loops dynamically compute all target permutations required by the strategy
    for movie in selected_movies:
        for age in target_ages:
            for interest in target_interests:
                # Request tailored text from the AI execution engine
                description = get_movie_recommendation(movie, age, interest)
                # Save each generated variant as an independent pending entity in the queue
                save_group_to_queue(age, interest, movie, description)
            
    # Redirect user to the verification page once generation loop finishes
    from flask import redirect, url_for
    return redirect(url_for('review'))

@app.route('/review')
def review():
    """Displays the moderation dashboard showing all un-sent templates."""
    # Fetch all currently pending templates from the SQLite database
    messages = get_current_queue()
    return render_template('review.html', messages=messages)

@app.route('/regenerate_message/<int:msg_id>', methods=['POST'])
def regenerate_message(msg_id):
    """Endpoint for asynchronous (AJAX) updates of a specific message by its unique ID."""
    conn = sqlite3.connect("movie_cache.db")
    cursor = conn.cursor()
    
    # Get parameters of the existing card to rewrite it with identical settings
    cursor.execute("SELECT age_group, interest, movie_name FROM delivery_queue WHERE id=?", (msg_id,))
    res = cursor.fetchone()
    
    if res:
        age, interest, movie = res
        # Run AI logic with force_refresh=True to bypass caching and get a new text variation
        new_desc = get_movie_recommendation(movie, age, interest, force_refresh=True)
        
        # Update the specific record text content in the queue table
        cursor.execute("UPDATE delivery_queue SET description=? WHERE id=?", (new_desc, msg_id))
        conn.commit()
        conn.close()
        # Return operational data back to the JavaScript frontend handler
        return jsonify({"status": "success", "new_description": new_desc})
            
    conn.close()
    return jsonify({"status": "error", "message": "Message not found"}), 400

@app.route('/send_all', methods=['POST'])
def send_all():
    """Simulates a mass personalized delivery campaign using the approved templates."""
    conn = sqlite3.connect("movie_cache.db")
    cursor = conn.cursor()
    
    # Grab all generated texts that are currently pending review
    cursor.execute("SELECT age_group, interest, movie_name, description FROM delivery_queue WHERE status='pending'")
    templates = cursor.fetchall()
    
    for age_group, interest, movie, desc in templates:
        # Dynamically query active clients matching this template's demographic segment
        cursor.execute("SELECT email FROM clients WHERE age_group=? AND interest=?", (age_group, interest))
        clients = cursor.fetchall()
        
        # Iterate over matching targeted user list and simulate email delivery to console
        for (email,) in clients:
            print(f"\n[REAL DELIVERY] To: {email} (Group: {age_group} | Interest: {interest})")
            print(f"[SUBJECT] Personalized Recommendation: {movie}")
            print(f"[CONTENT] {desc}")
    
    # Switch queue flags to 'sent' state to clear out the moderation dashboard grid
    cursor.execute("UPDATE delivery_queue SET status='sent' WHERE status='pending'")
    conn.commit()
    conn.close()
    
    return "<h1>🚀 Mass group delivery completed! Check your VS Code terminal server logs.</h1><a href='/'>To Main Page</a>"

if __name__ == '__main__':
    # Guarantee tables exist before initiating the live server run
    init_db()
    # Run server locally in debug mode to handle instant code hot-reloading
    app.run(debug=True)