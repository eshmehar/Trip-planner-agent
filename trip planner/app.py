from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from agent import run_agent
print(" app.py is starting...")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def index():
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, query, timestamp FROM reports ORDER BY timestamp DESC")
    reports = c.fetchall()
    conn.close()
    return render_template('index.html', reports=reports)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = run_agent(query)

    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, query, timestamp FROM reports ORDER BY timestamp DESC")
    reports = c.fetchall()
    conn.close()

    return render_template('index.html', reports=reports, message=result)

@app.route('/plan/<int:report_id>')
def view_plan(report_id):
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report = c.fetchone()
    conn.close()
    if report:
        return render_template('plan.html', report=report)
    else:
        return "Plan not found", 404

if __name__ == '__main__':
    app.run(debug=True)