from .shared import make_api_call

def generate_hypothesis(ontologist_insights):
    prompt = f"Based on the following insights, generate a research hypothesis: {ontologist_insights}"
    return make_api_call(prompt)
