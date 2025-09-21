import os
import sqlite3
import requests
from tavily import TavilyClient
from trafilatura import fetch_url, extract
import PyPDF2
from io import BytesIO
from groq import Groq 
import requests

os.environ["GROQ_API_KEY"] = "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"  
os.environ["TAVILY_API_KEY"] =  "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"
os.environ["OPENWEATHER_API_KEY"] = "d315b782ea3d74a87fd8241e13d62a49"

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# DATABASE setup
def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT,
                  summary TEXT,
                  sources TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

#  SEARCHES
def search_web(query):# uses tavily api to find 2-3 relevant sources
    try:
        response = tavily.search(query=query, max_results=3)
        return response['results']  # List of title
    except Exception as e:
        print("Search failed:", e)
        return []

# EXTRACT CONTENT in html 
def get_weather(city):
    """Get current weather for a city using OpenWeather API"""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key not set"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"{temp}°C, {desc}"
        else:
            return "Weather data unavailable"
    except Exception as e:
        return f"Weather error: {str(e)}"

# SUMMARIZES WITH LLM 
def generate_plan(goal, search_results, weather_info):
    prompt = f"""
    User goal: "{goal}"

    Web search results found:
    {search_results}

    Current weather info: {weather_info}

    Please create a clear, day-by-day plan to achieve this goal.
    Include specific activities, locations, and times if possible.
    Format:
    Day 1:
    - Activity 1 (Location, Time)
    - Activity 2 (Location, Time)

    Day 2:
    - ...

    Add practical tips based on weather or local info.
    """
    try:
        print(" GROQ API KEY:", os.environ.get("GROQ_API_KEY"))
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating plan: {e}"
#  SAVES
def save_report(query, summary, sources):# inserts all saved information into sqlite database
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute("INSERT INTO reports (query, summary, sources) VALUES (?, ?, ?)",
              (query, summary, str(sources)))
    conn.commit()
    report_id = c.lastrowid
    conn.close()
    return report_id

#  AGENT FUNCTION Runs everything
def run_agent(user_goal):
    print(" Planning goal:", user_goal)

    # Extract city for weather 
    city = None
    for word in user_goal.split():
        if word.lower() in ["jaipur", "hyderabad", "vizag", "delhi", "mumbai", "bangalore", "chennai", "kolkata"]:
            city = word
            break

    weather_info = get_weather(city) if city else "Weather info not available"

    # Search web for planning info
    results = search_web(user_goal)
    if not results:
        return "No planning info found. Try rephrasing."

    # Combine search results into text
    search_text = "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r.get('content', '')[:200]}..." for r in results[:3]])

    print(" Generating plan with LLM...")
    plan = generate_plan(user_goal, search_text, weather_info)

    print(" Saving to database...")
    # Save goal + plan + weather 
    sources = f"Weather: {weather_info} | URLs: " + ", ".join([r['url'] for r in results[:3]])
    report_id = save_report(user_goal, plan, sources)

    return f"Plan #{report_id} created!\n\n{plan}"
init_db()
