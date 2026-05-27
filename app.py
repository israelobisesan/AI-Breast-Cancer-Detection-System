import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ============================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================

# 1. PASTE YOUR GEMINI API KEY HERE
# Get it from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')

# 2. CHANGE THIS TO ANY RANDOM STRING
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-to-random-string')

# 3. Database file (you can leave this as default)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'breast_cancer_detector.db')

# ============================================
# END OF CONFIGURATION
# ============================================

# Configure Gemini API
if GEMINI_API_KEY == 'your-gemini-api-key-here':
    print("\n" + "="*60)
    print("⚠️  WARNING: Please set your GEMINI_API_KEY!")
    print("="*60)
    print("1. Get your FREE API key from:")
    print("   https://makersuite.google.com/app/apikey")
    print("2. Open app.py and paste it on line 18")
    print("3. Change 'your-gemini-api-key-here' to your actual key")
    print("="*60 + "\n")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')

# Symptoms from WHO and NHS documentation
SYMPTOMS = [
    {
        'id': 'lump',
        'text': 'Breast lump or thickening (often painless)',
        'weight': 25
    },
    {
        'id': 'skin_dimpling',
        'text': 'Dimpling, pitting or other skin changes (may look like orange peel)',
        'weight': 20
    },
    {
        'id': 'size_shape_change',
        'text': 'Change in size, shape or appearance of the breast',
        'weight': 15
    },
    {
        'id': 'nipple_discharge',
        'text': 'Abnormal or bloody fluid from the nipple',
        'weight': 20
    },
    {
        'id': 'nipple_change',
        'text': 'Change in nipple appearance (inversion, turning inward) or rash on nipple',
        'weight': 18
    },
    {
        'id': 'redness',
        'text': 'Redness or changes in breast skin color',
        'weight': 12
    },
    {
        'id': 'armpit_pain',
        'text': 'Pain in breast or armpit that does not go away',
        'weight': 10
    },
    {
        'id': 'armpit_lump',
        'text': 'Lump or swelling in armpit',
        'weight': 18
    },
    {
        'id': 'skin_texture',
        'text': 'Thickening or changes in skin texture',
        'weight': 12
    },
    {
        'id': 'nipple_position',
        'text': 'Change in position of nipple',
        'weight': 15
    }
]

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                gender TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                description TEXT,
                risk_percentage INTEGER NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.commit()
        db.close()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_risk_percentage(symptoms_selected, gender):
    """Calculate risk percentage based on symptoms"""
    if not symptoms_selected:
        return 10
    
    total_weight = 0
    for symptom_id in symptoms_selected:
        symptom = next((s for s in SYMPTOMS if s['id'] == symptom_id), None)
        if symptom:
            total_weight += symptom['weight']
    
    # Calculate base percentage
    max_possible_weight = sum(s['weight'] for s in SYMPTOMS)
    base_percentage = int((total_weight / max_possible_weight) * 100)
    
    # Adjust for number of symptoms (more symptoms = higher risk)
    symptom_count_factor = min(len(symptoms_selected) * 5, 20)
    
    # Male breast cancer is rare but when symptoms appear, should be taken seriously
    gender_adjustment = 5 if gender == 'male' and len(symptoms_selected) >= 2 else 0
    
    final_percentage = min(base_percentage + symptom_count_factor + gender_adjustment, 95)
    
    # Ensure minimum of 15% if any symptoms selected
    return max(final_percentage, 15)

def generate_ai_response(gender, symptoms_selected, description, risk_percentage, location):
    """Generate AI response using Gemini"""
    
    # Get symptom names
    symptom_names = []
    for symptom_id in symptoms_selected:
        symptom = next((s for s in SYMPTOMS if s['id'] == symptom_id), None)
        if symptom:
            symptom_names.append(symptom['text'])
    
    # Determine urgency level
    if risk_percentage >= 60:
        urgency = "THIS WEEK—don't wait"
        concern_level = "high"
    elif risk_percentage >= 40:
        urgency = "within the next 5-7 days"
        concern_level = "moderate"
    else:
        urgency = "within the next 1-2 weeks"
        concern_level = "lower"
    
    # Create comprehensive system prompt
    system_prompt = f"""
You are an AI-powered breast health awareness and healthcare guidance assistant.

Your purpose is to:
- help users understand breast-related symptoms,
- encourage appropriate medical evaluation,
- provide calm educational guidance,
- recommend nearby healthcare facilities when available,
- and help users take the next appropriate healthcare step.

IMPORTANT SAFETY RULES:
- You are NOT a doctor.
- You do NOT diagnose breast cancer.
- You do NOT confirm whether a user has cancer.
- You must NEVER provide fake certainty or invented medical probabilities.
- You must NEVER hallucinate hospitals, prices, medical services, or free screening programs.
- If healthcare pricing or availability is uncertain, clearly say:
  "Pricing information could not be verified. Please contact the hospital or clinic directly."

PATIENT INFORMATION:
- Gender: {gender.capitalize()}
- Symptoms Reported: {', '.join(symptom_names)}
- Additional Description: "{description if description else 'No additional details provided'}"
- Concern Level: {risk_percentage}
- User Location: {location if location else 'Unknown'}

YOUR RESPONSE SHOULD:

1. Acknowledge the user's concern calmly and professionally.

2. Explain that some reported symptoms can sometimes be associated with breast conditions, including breast cancer, but symptoms alone cannot confirm a diagnosis.

3. Use cautious language such as:
- "may"
- "can sometimes"
- "could be associated with"

NEVER say:
- "you have cancer"
- "you likely have cancer"
- exact cancer percentages
- "coin flip"
- emotionally dramatic phrases

4. Explain possible non-cancerous causes where appropriate, including:
- breast cysts
- hormonal changes
- fibroadenomas
- fibrocystic breast changes
- mastitis
- gynecomastia (for male users)

5. Recommend medical evaluation using the assigned concern level:
- Lower Concern:
  "A routine medical check-up is recommended if symptoms persist."
- Moderate Concern:
  "A medical review is recommended within the next several days."
- Elevated Concern:
  "Prompt medical evaluation is recommended."

6. Recommend next steps:
- Clinical breast examination
- Mammogram and/or ultrasound depending on physician recommendation
- Additional testing if required by a healthcare professional

7. If nearby hospitals or screening centers are available:
- Suggest reputable hospitals or clinics nearby
- Mention free or low-cost screening programs ONLY if verified
- Mention approximate pricing ONLY if verified
- If uncertain, explicitly say pricing could not be verified

8. End with supportive but calm encouragement.

STYLE REQUIREMENTS:
- Professional
- Calm
- Human
- Clear
- Non-dramatic
- Easy to understand
- Educational

LENGTH:
200–500 words.

REMEMBER:
This system is a symptom awareness and healthcare navigation tool — NOT a cancer diagnosis system.
"""
    try:
        response = model.generate_content(system_prompt)
        clean = response.text.replace('**', '')
        return clean
    except Exception as e:
        app.logger.error(f"Gemini API error: {e}")
        # Fallback response if API fails
        return generate_fallback_response(risk_percentage, gender, len(symptoms_selected))

def generate_fallback_response(risk_percentage, gender, symptom_count):
    """Fallback response if AI API fails"""
    if risk_percentage >= 60:
        urgency = "THIS WEEK - don't wait"
        concern_level = "high"
    elif risk_percentage >= 40:
        urgency = "within the next 5-7 days"
        concern_level = "moderate"
    else:
        urgency = "within the next 1-2 weeks"
        concern_level = "lower"
    
    male_note = " As a man, any breast symptoms should be taken seriously, even though male breast cancer is rare (less than 1% of cases)." if gender == 'male' else ""
    
    return f"""Hey, thanks for trusting me with this. I've looked at everything you've shared.

Based on what you've told me, there's approximately a {risk_percentage}% chance this could be breast cancer.

You've reported {symptom_count} symptom{"s" if symptom_count != 1 else ""}, and according to WHO guidelines, this warrants medical attention.{male_note}

Here's what you need to do:

Please see a doctor {urgency}. They'll likely want to:
- Perform a clinical breast examination
- Order imaging tests (mammogram and/or ultrasound)
- Possibly do a biopsy depending on findings

Remember, even if this is breast cancer, early detection makes a huge difference in treatment outcomes. You're doing the right thing by getting this checked out.

Take care, and please don't delay making that appointment. 💙

IMPORTANT: This is NOT a medical diagnosis. Only a qualified healthcare professional can diagnose breast cancer through proper examination and testing."""

@app.route('/')
def index():
    """Landing page with breast cancer information"""
    return render_template('index.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    """Symptom assessment form"""
    if request.method == 'POST':
        # Get form data
        gender = request.form.get('gender')
        symptoms_selected = request.form.getlist('symptoms')
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate input
        if not gender:
            flash('Please select your gender.', 'error')
            return redirect(url_for('assessment'))
        
        if not symptoms_selected:
            flash('Please select at least one symptom.', 'error')
            return redirect(url_for('assessment'))
        
        # Calculate risk percentage
        risk_percentage = calculate_risk_percentage(symptoms_selected, gender)
        
        # Generate AI response
        ai_response = generate_ai_response(gender, symptoms_selected, description, risk_percentage, location)
        
        # Store in session for results page
        session['last_assessment'] = {
            'gender': gender,
            'symptoms': symptoms_selected,
            'location': location,
            'description': description,
            'risk_percentage': risk_percentage,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        
        return redirect(url_for('results'))
    
    return render_template('assessment.html', symptoms=SYMPTOMS)

@app.route('/results')
def results():
    """Display assessment results"""
    assessment_data = session.get('last_assessment')
    
    if not assessment_data:
        flash('No assessment found. Please complete the form first.', 'warning')
        return redirect(url_for('assessment'))
    
    # Check if user is logged in
    is_logged_in = 'user_id' in session
    
    return render_template('results.html', 
                         assessment=assessment_data, 
                         is_logged_in=is_logged_in)

@app.route('/save-result', methods=['POST'])
@login_required
def save_result():
    """Save assessment result to database"""
    assessment_data = session.get('last_assessment')
    
    if not assessment_data:
        return jsonify({'success': False, 'message': 'No assessment to save'})
    
    try:
        db = get_db()
        db.execute('''
            INSERT INTO assessments (user_id, gender, symptoms, description, risk_percentage, ai_response)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            assessment_data['gender'],
            json.dumps(assessment_data['symptoms']),
            assessment_data['description'],
            assessment_data['risk_percentage'],
            assessment_data['ai_response']
        ))
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'message': 'Assessment saved successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error saving assessment'})

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing assessment history"""
    db = get_db()
    assessments = db.execute('''
        SELECT * FROM assessments 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    db.close()
    
    # Convert to list of dicts
    assessment_list = []
    for assessment in assessments:
        assessment_list.append({
            'id': assessment['id'],
            'gender': assessment['gender'],
            'symptoms': json.loads(assessment['symptoms']),
            'description': assessment['description'],
            'risk_percentage': assessment['risk_percentage'],
            'ai_response': assessment['ai_response'],
            'created_at': assessment['created_at']
        })
    
    return render_template('dashboard.html', assessments=assessment_list, symptoms=SYMPTOMS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('register'))
        
        # Check if user exists
        db = get_db()
        existing_user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            db.close()
            return redirect(url_for('login'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        cursor = db.execute('INSERT INTO users (email, password) VALUES (?, ?)', 
                          (email, hashed_password))
        db.commit()
        
        # Log user in
        session['user_id'] = cursor.lastrowid
        session['user_email'] = email
        
        db.close()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            flash('Login successful!', 'success')
            
            # Redirect to dashboard or previous page
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)