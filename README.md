# Trip-planner-agent
A trip planner agent which could plan a trip according to the information feeded to it
This project is a Trip Planner AI Agent that transforms natural language goals — like “Plan a 3-day trip to Jaipur” — into structured, day-by-day itineraries enriched with real-time context.
• Searches the web via Tavily API to find attractions, restaurants, and local tips relevant to the user’s goal.
• Fetches live weather using OpenWeather API to add practical, location-specific advice (e.g., “32°C and sunny — carry sunscreen”).
• Generates human-readable plans using Groq’s Llama 3.1 model, formatting output as clear, actionable steps with times and locations.
• Saves every plan to a local SQLite database for future reference and revisiting.
• Displays plans in a clean Flask web UI, allowing users to generate new trips or browse past itineraries with one click.
Built entirely in Python, this agent demonstrates a production-style, tool-using AI system — chaining search, weather, LLM, storage, and UI into one seamless, locally-run application — with no credit card required.
