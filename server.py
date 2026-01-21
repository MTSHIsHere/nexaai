# server.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load model
tokenizer = AutoTokenizer.from_pretrained("./models")
model = AutoModelForCausalLM.from_pretrained("./models")

# In-memory user storage (simples, só pra teste)
users = {}

@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/')
        return "Invalid login"
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists"
        users[username] = password
        session['user'] = username
        return redirect('/')
    return render_template('signup.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    prompt = request.json['prompt']
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
