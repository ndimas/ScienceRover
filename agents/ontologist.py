from .shared import make_api_call

def analyze(graph):
    prompt = f"Analyze the following graph and provide insights about the relationships between concepts: {graph.edges()}"
    return make_api_call(prompt)
