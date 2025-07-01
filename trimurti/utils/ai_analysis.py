import requests
import re

def format_ai_markdown(text):
    """
    Post-process AI output to ensure markdown-style formatting for headings and lists.
    - Bold section headings (Key Findings, Potential Risks, Actionable Recommendations, Conclusion, etc.)
    - Convert lines starting with numbers, dashes, or asterisks to lists
    """
    # Bold common headings
    headings = [
        'Key Findings', 'Potential Risks', 'Actionable Recommendations', 'Conclusion',
        'Executive Summary', 'Detailed Technical Findings', 'Security Recommendations',
        'Complete Subdomain Inventory', 'SSL/TLS Configuration Analysis', 'Findings', 'Summary'
    ]
    for heading in headings:
        text = re.sub(rf'^(\s*)\*?\*?{re.escape(heading)}\*?\*?:?\s*$', rf'\1**{heading}:**', text, flags=re.MULTILINE|re.IGNORECASE)
    # Convert numbered lists (preserve actual numbers)
    text = re.sub(r'^(\s*)(\d+)\.\s+', r'\1\2. ', text, flags=re.MULTILINE)
    # Convert dash lists
    text = re.sub(r'^(\s*)[-•]\s+', r'\1- ', text, flags=re.MULTILINE)
    # Convert asterisk lists
    text = re.sub(r'^(\s*)\*\s+', r'\1- ', text, flags=re.MULTILINE)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def analyze_recon_output(data):
    """
    Analyze reconnaissance output (e.g., subdomain discovery) using Ollama Llama 3 model.
    The LLM should act as a cybersecurity expert and provide a human-readable, professional summary with actionable insights, using clear formatting and markdown-style sections.
    """
    prompt = (
        "You are a cybersecurity expert writing a professional penetration test report. "
        "Analyze the following reconnaissance output and provide a well-structured, human-readable summary. "
        "Format your response using markdown syntax with bold headings (e.g., **Key Findings**, **Potential Risks**, **Actionable Recommendations**, **Conclusion**). "
        "Use bullet points (-) or numbered lists (1., 2., etc.) for findings and recommendations. "
        "Here is an example format:\n\n"
        "**Key Findings:**\n- Finding 1\n- Finding 2\n\n"
        "**Potential Risks:**\n1. Risk 1\n2. Risk 2\n\n"
        "**Actionable Recommendations:**\n- Recommendation 1\n- Recommendation 2\n\n"
        "**Conclusion:**\nSummary statement here.\n\n"
        "Now, analyze the following reconnaissance output:\n"
        f"{data}\n\n"
        "Summary:"
    )
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    raw = response.json().get("response", "[No response from Ollama]")
    return format_ai_markdown(raw)

def analyze_vulnerabilities(data):
    """
    Analyze vulnerability scan output using Ollama Llama 3 model.
    """
    prompt = (
        "You are a cybersecurity expert writing a professional penetration test report. "
        "Analyze the following vulnerability scan results and provide a well-structured, human-readable summary. "
        "Format your response using markdown syntax with bold headings (e.g., **Key Findings**, **Potential Risks**, **Actionable Recommendations**, **Conclusion**). "
        "Use bullet points (-) or numbered lists (1., 2., etc.) for findings and recommendations. "
        "Here is an example format:\n\n"
        "**Key Findings:**\n- Finding 1\n- Finding 2\n\n"
        "**Potential Risks:**\n1. Risk 1\n2. Risk 2\n\n"
        "**Actionable Recommendations:**\n- Recommendation 1\n- Recommendation 2\n\n"
        "**Conclusion:**\nSummary statement here.\n\n"
        "Now, analyze the following vulnerability scan results:\n"
        f"{data}\n\n"
        "Summary:"
    )
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    raw = response.json().get("response", "[No response from Ollama]")
    return format_ai_markdown(raw)

