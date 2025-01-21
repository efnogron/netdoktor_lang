"""Prompts used in the retrieval process."""

QUERY_ANALYSIS_PROMPT = """Analyze the following query and identify the key medical concepts:
Query: {query}

Focus on identifying:
1. Medical conditions
2. Medications
3. Treatment contexts (e.g., pregnancy, pediatric)
4. Specific guidelines being referenced

Provide a concise analysis that will help in retrieving relevant medical guideline sections."""

RESULT_SYNTHESIS_PROMPT = """Based on the retrieved guideline sections, provide a comprehensive answer:

Query: {query}

Retrieved Sections:
{context}

Your task is to verify the statement in the query. Output a boolean value (True or False) and a short explanation. Provide a corrected statement if the statement is not correct.
""" 