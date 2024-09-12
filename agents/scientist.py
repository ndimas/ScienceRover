from .shared import make_api_call

def generate_hypothesis(ontologist_insights, papers):
    paper_summaries = "\n".join([f"Title: {paper['title']}\nAbstract: {paper['abstract']}" for paper in papers[:3]])
    prompt = f"""Based on the following insights and relevant papers, generate a detailed research hypothesis:

Ontologist Insights:
{ontologist_insights}

Relevant Papers:
{paper_summaries}

Generate a comprehensive research hypothesis that incorporates the concepts from the ontologist insights and builds upon the findings from the relevant papers. Your response should be structured as follows:

1. Research Question: Clearly state the main research question or problem to be addressed.
2. Hypothesis: Provide a detailed hypothesis that answers the research question.
3. Methodology: Outline the proposed methods to test the hypothesis, including any specific techniques or experiments.
4. Expected Outcomes: Describe the anticipated results and their potential significance.
5. Potential Impact: Explain how this research could contribute to the field and its broader implications.

Ensure that your hypothesis is innovative, grounded in existing research, and proposes a novel direction for investigation. Be as specific and quantitative as possible, including any relevant numbers, material properties, or chemical formulas where appropriate."""
    
    return make_api_call(prompt)
