# 🎀 Breast Cancer Detection System

An AI-powered breast cancer symptom assessment tool that provides personalized risk analysis and medical guidance based on WHO and NHS clinical guidelines.

## 🌟 Features

### Core Functionality

- ✅ **AI-Powered Assessment** - Uses Google Gemini API for intelligent symptom analysis
- ✅ **Risk Percentage Calculation** - Visual progress bar showing breast cancer risk (0-100%)
- ✅ **Conversational AI Responses** - Empathetic, doctor-like responses with personalized advice
- ✅ **10 Clinical Symptoms** - Based on WHO and NHS guidelines
- ✅ **Gender-Specific Analysis** - Separate logic for male and female breast cancer

### User Features

- 🔓 **Guest Mode** - Use without creating an account (results not saved)
- 🔐 **Optional Login** - Create account to save results and view history
- 📊 **Dashboard** - Track assessments over time for logged-in users
- 🎨 **Beautiful UI** - White, blue, and soft pink color scheme
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

### Safety Features

- ⚠️ **Medical Disclaimers** - Clear warnings that this is not a diagnosis
- 🔒 **Privacy-Focused** - Guest mode for anonymous use
- 💙 **Compassionate Tone** - Reduces anxiety while providing honest information

## 🎨 Color Scheme

- **White** (#FFFFFF) - Clean backgrounds
- **Primary Blue** (#4A90E2) - Buttons, progress bars, headers
- **Soft Pink** (#FFB6C1) - Accents, breast cancer awareness ribbon 🎀
- **Light Blue** (#E3F2FD) - Card backgrounds, highlights

## 📋 Requirements

- Python 3.8+
- Flask
- Google Gemini API key (FREE tier available)
- SQLite (included with Python)

## 🚀 Installation & Setup

### Step 1: Clone or Download

```bash
cd breast_cancer_detector
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get Gemini API Key (FREE)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 4: Configure API Key

**Option A: Environment Variable (Recommended)**

```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Option B: Edit app.py**
Open `app.py` and replace:

```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-api-key-here')
```

With:

```python
GEMINI_API_KEY = 'your-actual-api-key-here'
```

### Step 5: Change Secret Key

In `app.py`, change:

```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

To a random string (for security):

```python
app.secret_key = 'your-random-secret-key-xyz123'
```

### Step 6: Run the Application

```bash
python app.py
```

The app will start on: **http://localhost:5000**

## 📁 Project Structure

```
breast_cancer_detector/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── breast_cancer_detector.db       # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css              # Main stylesheet
│   └── js/
│       └── main.js                # JavaScript functionality
└── templates/
    ├── base.html                  # Base template with navigation
    ├── index.html                 # Landing page
    ├── assessment.html            # Symptom form
    ├── results.html               # AI assessment results with progress bar
    ├── dashboard.html             # User dashboard (logged-in)
    ├── login.html                 # Login page
    └── register.html              # Registration page
```

## 🔧 How It Works

### 1. Symptom Collection

User selects symptoms from 10 clinical indicators:

- Breast lump or thickening
- Skin dimpling or changes
- Size/shape changes
- Nipple discharge
- Nipple changes (inversion, rash)
- Redness
- Pain in breast/armpit
- Armpit lump
- Skin texture changes
- Nipple position changes

### 2. Risk Calculation

The system calculates risk percentage based on:

- Weighted symptom scoring
- Number of symptoms
- Gender (male breast cancer is rare but serious)
- Clinical significance per WHO guidelines

### 3. AI Analysis

Google Gemini API generates:

- Risk percentage explanation
- Symptom interpretation
- Differential diagnosis (cancer vs. other conditions)
- Urgency recommendations
- Next steps and advice

### 4. Response Guidelines

- **60-100% risk**: Urgent - see doctor THIS WEEK
- **40-59% risk**: Moderate - see doctor within 5-7 days
- **0-39% risk**: Lower concern - see doctor within 1-2 weeks

## 🎯 Usage Examples

### Guest Mode (No Login)

1. Go to homepage
2. Click "Start Assessment"
3. Select gender and symptoms
4. Get instant AI analysis
5. Results disappear after session

### Registered User

1. Create free account
2. Complete assessment
3. Click "Save Result"
4. View all past assessments in Dashboard
5. Track symptoms over time

## 🔐 Security & Privacy

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Management**: Flask-Login for secure sessions
- **SQLite Database**: Local storage, no external database required
- **Guest Mode**: No data stored for anonymous users
- **HTTPS Recommended**: Use HTTPS in production

## 🌍 Deployment

### For Production:

1. Change `app.secret_key` to a strong random string
2. Set `debug=False` in `app.run()`
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Enable HTTPS
5. Set proper environment variables
6. Use PostgreSQL instead of SQLite for better performance

### Example with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 API Costs (Gemini FREE Tier)

- **Free Tier**: 15 requests/min, 1,500 requests/day
- **Cost per request**: $0.00 (FREE)
- **Upgrade**: If you exceed free tier, costs are ~$0.075 per million tokens

For 1,000 users/day on FREE tier = **$0.00**

## 🔄 Switching to Other AI APIs

The code is designed for easy API switching:

### To use OpenAI GPT-4o-mini:

```python
import openai
openai.api_key = 'your-openai-key'

def generate_ai_response(...):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}]
    )
    return response.choices[0].message.content
```

### To use Claude:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-claude-key")

def generate_ai_response(...):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": system_prompt}]
    )
    return message.content[0].text
```

## ⚠️ Important Medical Disclaimer

**THIS TOOL DOES NOT DIAGNOSE BREAST CANCER.**

This is an educational and informational tool only. It:

- ❌ Cannot replace professional medical examination
- ❌ Cannot diagnose breast cancer
- ❌ Should not be used to make medical decisions
- ✅ Can help users understand when to seek medical care
- ✅ Provides symptom education based on WHO/NHS guidelines

**Always consult a qualified healthcare professional for medical advice.**

## 📖 Data Sources

All symptom information is based on:

- **WHO** (World Health Organization) - Breast Cancer Fact Sheet
- **NHS** (UK National Health Service) - Breast Cancer Symptoms
- Clinical guidelines for breast cancer detection

## 🤝 Contributing

This is an educational project. Improvements welcome:

- Better AI prompts for more accurate responses
- Additional symptoms from clinical research
- Multi-language support
- Accessibility improvements

## 📝 License

This project is for educational purposes. Please ensure compliance with medical regulations in your region before deploying publicly.

## 🆘 Support

For issues or questions:

1. Check this README
2. Review the code comments
3. Test with Gemini API key properly configured
4. Verify Python dependencies are installed

## 🎓 Educational Use

Perfect for:

- Medical informatics students
- Health tech hackathons
- AI in healthcare demonstrations
- Breast cancer awareness campaigns

## 📞 Emergency Resources

If you have concerning symptoms:

- **USA**: Call your doctor or 911
- **UK**: Call NHS 111 or 999
- **International**: Contact local emergency services

**Early detection saves lives. Don't delay seeking medical care.** 💙

---

Made with 💙 for breast cancer awareness and early detection.
