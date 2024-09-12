from .shared import make_api_call

def review(hypothesis):
    prompt = f"Review and provide feedback on the following research hypothesis: {hypothesis}"
    return make_api_call(prompt)
