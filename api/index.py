import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def scrape_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        text_content = ' '.join(paragraphs[:5])
        return f"Title: {title}. Context: {text_content[:800]}"
    except Exception as e:
        return f"Website content summary: Tech company in B2B sector."

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    prospect_url = data.get('url', '')
    prospect_role = data.get('role', 'Decision Maker')
    my_offer = data.get('offer', 'AI Automation Services')

    if not prospect_url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    scraped_context = scrape_website(prospect_url)

    prompt = f"""
    You are an elite B2B Sales Specialist. Write a short, personalized, ultra-high-converting cold email.
    
    Prospect Website Context: {scraped_context}
    Prospect Role: {prospect_role}
    Our Service/Value Prop: {my_offer}
    
    Guidelines:
    - Subject Line: Catchy, under 5 words, lowercase feel.
    - Opening Line: Specific observation about their business based on context.
    - Pitch: Bridge their need to our offer in 2 concise sentences.
    - Call to Action (CTA): Low friction (e.g., "Open to a 3-min chat this Thursday?").
    - Tone: Professional, direct, non-spammy.
    """

    try:
        if not GEMINI_API_KEY:
            email_output = f"Subject: quick thought on {prospect_url}\n\nHi there,\n\nNoticed your work at {prospect_url}. Most {prospect_role}s are currently struggling to streamline operations.\n\nWe help companies scale faster using {my_offer}.\n\nWorth a brief 5-min chat this week?"
        else:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            email_output = response.text

        return jsonify({'result': email_output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OutreachAI — OLED Cold Email Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        oled: '#000000',
                        cardBg: '#09090b',
                        borderClr: '#27272a',
                        accent: '#6366f1'
                    }
                }
            }
        }
    </script>
    <style>
        .dot-flashing {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .dot-flashing span {
            width: 6px;
            height: 6px;
            background-color: #a1a1aa;
            border-radius: 50%;
            animation: dotPulse 1.4s infinite ease-in-out both;
        }
        .dot-flashing span:nth-child(1) { animation-delay: -0.32s; }
        .dot-flashing span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes dotPulse {
            0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
            40% { transform: scale(1); opacity: 1; }
        }
    </style>
</head>
<body class="bg-oled text-zinc-100 min-h-screen flex flex-col justify-between font-sans antialiased">
    
    <!-- Header -->
    <header class="border-b border-borderClr py-4 px-6 bg-black/50 backdrop-blur-md sticky top-0 z-50 flex justify-between items-center">
        <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-indigo-500 animate-pulse"></div>
            <span class="font-bold text-lg tracking-wider text-white">OUTREACH<span class="text-indigo-500">.AI</span></span>
        </div>
        <span class="text-xs bg-zinc-800 text-zinc-400 px-3 py-1 rounded-full border border-zinc-700">Enterprise v1.0</span>
    </header>

    <!-- Main Container -->
    <main class="max-w-4xl mx-auto w-full px-4 py-8 flex-grow">
        <div class="text-center mb-8">
            <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight mb-3">Personalize Cold Outreach in Seconds</h1>
            <p class="text-zinc-400 text-sm md:text-base">Scrape prospect insights & generate high-converting B2B sales emails instantly.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Left Panel: Input -->
            <div class="bg-cardBg border border-borderClr rounded-xl p-6 shadow-2xl">
                <h2 class="text-sm font-semibold text-zinc-300 uppercase tracking-wider mb-4 flex items-center">
                    <span class="mr-2">⚙️</span> Campaign Parameters
                </h2>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-medium text-zinc-400 mb-1">Prospect Website URL</label>
                        <input type="text" id="url" placeholder="https://stripe.com" class="w-full bg-black border border-borderClr rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-zinc-400 mb-1">Prospect Role / Title</label>
                        <input type="text" id="role" placeholder="Head of Growth / Founder" class="w-full bg-black border border-borderClr rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-zinc-400 mb-1">Your Value Offer</label>
                        <input type="text" id="offer" placeholder="Custom AI Lead Generation Tool" class="w-full bg-black border border-borderClr rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
                    </div>
                    <button onclick="generateEmail()" id="btn" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg text-sm transition duration-200 shadow-lg shadow-indigo-500/20 flex justify-center items-center">
                        Generate Personalized Email
                    </button>
                </div>
            </div>

            <!-- Right Panel: Clean Output without Inner Box -->
            <div class="bg-cardBg border border-borderClr rounded-xl p-6 flex flex-col justify-between shadow-2xl min-h-[320px]">
                <div>
                    <h2 class="text-sm font-semibold text-zinc-300 uppercase tracking-wider mb-4 flex items-center">
                        <span class="mr-2">⚡</span> AI Generated Output
                    </h2>
                    
                    <!-- Clean, natural text display -->
                    <div id="output" class="text-zinc-200 text-base leading-relaxed whitespace-pre-wrap font-sans">
                        Result will appear here...
                    </div>
                </div>
                <div class="mt-6 flex justify-end">
                    <button onclick="copyText()" class="text-xs text-zinc-400 hover:text-white flex items-center space-x-1">
                        <span>📋 Copy Output</span>
                    </button>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-borderClr py-4 text-center text-xs text-zinc-600">
        © 2026 OutreachAI. Built for High-Ticket B2B Sales.
    </footer>

    <script>
        async function generateEmail() {
            const url = document.getElementById('url').value;
            const role = document.getElementById('role').value;
            const offer = document.getElementById('offer').value;
            const btn = document.getElementById('btn');
            const output = document.getElementById('output');

            if (!url) {
                alert('Please enter a Prospect Website URL');
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Scraping & Generating...';
            output.innerHTML = '<div class="dot-flashing"><span></span><span></span><span></span></div>';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, role, offer })
                });

                const data = await response.json();
                if (data.result) {
                    output.innerText = data.result;
                } else {
                    output.innerText = 'Error: ' + (data.error || 'Failed to generate');
                }
            } catch (err) {
                output.innerText = 'Error connecting to server.';
            } finally {
                btn.disabled = false;
                btn.innerText = 'Generate Personalized Email';
            }
        }

        function copyText() {
            const text = document.getElementById('output').innerText;
            if(!text || text === 'Result will appear here...') return;
            navigator.clipboard.writeText(text);
            alert('Copied to clipboard!');
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
    
