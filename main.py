from flask import Flask, render_template, request, jsonify, Response
from agents import ontologist, scientist, critic
import networkx as nx
import json
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_hypothesis', methods=['POST'])
def generate_hypothesis():
    concepts = request.json['concepts']
    
    # Log the input
    logging.info(f"Received request for hypothesis generation with concepts: {concepts}")
    
    # Create a simple graph
    G = nx.Graph()
    G.add_edges_from([(concepts[i], concepts[i+1]) for i in range(len(concepts)-1)])
    
    def generate():
        yield "data: " + json.dumps({"stage": "ontologist", "content": ""}) + "\n\n"
        onto_result = ontologist.analyze(G)
        yield "data: " + json.dumps({"stage": "ontologist", "content": onto_result}) + "\n\n"
        
        yield "data: " + json.dumps({"stage": "scientist", "content": ""}) + "\n\n"
        scientist_result = scientist.generate_hypothesis(onto_result)
        yield "data: " + json.dumps({"stage": "scientist", "content": scientist_result}) + "\n\n"
        
        yield "data: " + json.dumps({"stage": "critic", "content": ""}) + "\n\n"
        critic_result = critic.review(scientist_result)
        yield "data: " + json.dumps({"stage": "critic", "content": critic_result}) + "\n\n"
        
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
