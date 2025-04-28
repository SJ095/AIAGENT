<h1>App Sentiment Analysis</h1>

<p>Analyze user reviews and sentiments for any app directly from the Google Play Store.</p>

<h2>Project Structure</h2>

<ul>
  <li><strong>Frontend:</strong> React.js (Next.js)</li>
  <li><strong>Backend:</strong> FastAPI (Python)</li>
  <li><strong>Sentiment Analysis:</strong> Ollama API (using Mistral model)</li>
</ul>

<h2>Setup Instructions</h2>

<h3>1. Backend Setup (FastAPI)</h3>

<h4>Requirements:</h4>
<ul>
  <li>Python 3.9+</li>
  <li>Virtual environment (optional but recommended)</li>
</ul>

<h4>Steps:</h4>

<pre><code># Clone the repository
git clone https://github.com/SJ095/AIAGENT

# Navigate to backend folder
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn google-play-scraper ollama

# Start FastAPI server
uvicorn main:app --reload
</code></pre>

<p>Backend will run at <code>http://localhost:8000</code>.</p>

<h3>2. Frontend Setup (React - Next.js)</h3>

<h4>Requirements:</h4>
<ul>
  <li>Node.js 18+</li>
</ul>

<h4>Steps:</h4>

<pre><code># Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
</code></pre>

<p>Frontend will run at <code>http://localhost:3000</code>.</p>

<h3>3. Project Notes</h3>

<ul>
  <li>Ensure that <code>backend</code> and <code>frontend</code> run simultaneously.</li>
  <li>A CORS middleware is already enabled to allow requests from <code>localhost:3000</code> to <code>localhost:8000</code>.</li>
  <li>The background image <code>back.jpeg</code> should be placed inside the <code>public/</code> folder of your frontend.</li>
</ul>

<h3>4. Important Files</h3>

<ul>
  <li><code>backend/main.py</code>: FastAPI app backend logic.</li>
  <li><code>frontend/app/page.js</code>: Frontend React component.</li>
</ul>

<h3>5. Usage</h3>

<ul>
  <li>Enter an app name in the input box.</li>
  <li>Autocomplete suggestions appear.</li>
  <li>Select an app or type manually.</li>
  <li>View average sentiment score and detailed review analysis.</li>
</ul>

<hr>

<h2>Troubleshooting</h2>

<ul>
  <li>If API calls are blocked due to CORS, check if backend CORS settings allow frontend origin.</li>
  <li>If Ollama API fails, ensure your model name (<code>mistral</code>) is properly installed and accessible.</li>
  <li>If search returns no apps, verify your internet connection and query spelling.</li>
</ul>

<hr>
