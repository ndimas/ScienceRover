from flask import Flask, render_template, request, jsonify, Response
from agents import ontologist, scientist, critic
from agents.graph_reasoning import analyze_graph
import networkx as nx
import json
import logging
import requests
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    return render_template('index.html')

def fetch_papers(concepts, limit=5):
    papers = []
    for concept in concepts:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={concept}&limit={limit}&fields=title,abstract,url"
        try:
            response = requests.get(url)
            response.raise_for_status()
            papers.extend(response.json().get('data', []))
        except requests.RequestException as e:
            logging.error(f"Error fetching papers for concept '{concept}': {str(e)}")
    return papers

@app.route('/generate_hypothesis', methods=['POST'])
def generate_hypothesis():
    text = request.json['text']
    
    # Log the input
    logging.info(f"ScienceRover: Received request for hypothesis generation with text: {text}")
    
    # Extract concepts using spaCy
    concepts = ontologist.extract_concepts(text)
    
    # Create a simple graph
    G = nx.Graph()
    G.add_edges_from([(concepts[i], concepts[i+1]) for i in range(len(concepts)-1)])
    
    # Fetch relevant papers
    papers = fetch_papers(concepts)
    
    def generate():
        try:
            yield "data: " + json.dumps({"stage": "concept_extraction", "content": ", ".join(concepts)}) + "\n\n"
            
            yield "data: " + json.dumps({"stage": "graph_analysis", "content": ""}) + "\n\n"
            graph_analysis = analyze_graph(G)
            yield "data: " + json.dumps({"stage": "graph_analysis", "content": json.dumps(graph_analysis, default=str)}) + "\n\n"
            
            yield "data: " + json.dumps({"stage": "ontologist", "content": ""}) + "\n\n"
            onto_result = ontologist.analyze(G)
            yield "data: " + json.dumps({"stage": "ontologist", "content": onto_result}) + "\n\n"
            
            yield "data: " + json.dumps({"stage": "scientist", "content": ""}) + "\n\n"
            scientist_result = scientist.generate_hypothesis(onto_result, papers)
            yield "data: " + json.dumps({"stage": "scientist", "content": scientist_result}) + "\n\n"
            
            yield "data: " + json.dumps({"stage": "critic", "content": ""}) + "\n\n"
            critic_result = critic.review(scientist_result)
            yield "data: " + json.dumps({"stage": "critic", "content": critic_result}) + "\n\n"
            
            # Log successful completion
            logging.info(f"ScienceRover: Successfully generated hypothesis for text: {text}")
        except Exception as e:
            error_message = f"An error occurred during hypothesis generation: {str(e)}"
            logging.error(error_message)
            yield "data: " + json.dumps({"stage": "error", "content": error_message}) + "\n\n"
        
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
