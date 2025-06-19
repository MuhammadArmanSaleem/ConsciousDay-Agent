from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import os
from dotenv import load_dotenv
load_dotenv()

# Use Together's OpenAI-compatible endpoint

llm = ChatTogether(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.7,
    together_api_key=os.getenv("TOGETHER_API_KEY")
)

prompt_template = PromptTemplate(
    input_variables=["journal", "dream", "intention", "priorities"],
    template="""
You are a daily reflection and planning assistant. Your goal is to:
1. Reflect on the user's journal and dream input
2. Interpret the user's emotional and mental state
3. Understand their intention and 3 priorities
4. Generate a practical, energy-aligned strategy for their day

INPUT:
Morning Journal: {journal}
Dream: {dream}
Intention: {intention}
Top 3 Priorities: {priorities}

OUTPUT:
1. Inner Reflection Summary
2. Dream Interpretation Summary
3. Energy/Mindset Insight
4. Suggested Day Strategy (time-aligned tasks)
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

def analyze_inputs(journal, dream, intention, priorities):
    response = chain.run({
        "journal": journal,
        "dream": dream,
        "intention": intention,
        "priorities": priorities
    })

    # Prepare default sections
    sections = {
        "reflection": "",
        "dream": "",
        "mindset": "",
        "strategy": ""
    }

    # Match and extract each labeled section
    matches = re.findall(r'\d\.\s*(.*?)\n(.*?)(?=\n\d\.|\Z)', response, re.DOTALL)

    for label, content in matches:
        label = label.strip().lower()
        if "reflection" in label:
            sections["reflection"] = content.strip()
        elif "dream" in label:
            sections["dream"] = content.strip()
        elif "mindset" in label or "energy" in label:
            sections["mindset"] = content.strip()
        elif "strategy" in label:
            sections["strategy"] = content.strip()

    return sections
