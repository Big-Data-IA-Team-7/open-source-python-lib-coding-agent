import re
from openai import OpenAI
from parameter_config import OPENAI_API

def clean_and_normalize_code(code_content: str) -> str:
    lines = code_content.splitlines()
    if lines:
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        min_indent = min(indents) if indents else 0
        lines = [line[min_indent:] if line.strip() else line for line in lines]
    return '\n'.join(lines)

def determine_file_extension(code_content: str) -> str:
    py_indicators = [r'\bdef\b', r'\bclass\b', r'\bimport\b', r'\bself\b', r':\s*$', r'from\s+\w+\s+import', r'__\w+__']
    bash_indicators = [r'^#!/bin/bash', r'^#!/usr/bin/env\s+bash', r'\becho\b', r'\bls\b', r'\bgrep\b', r'\bcat\b', r'\bsed\b', r'\bawk\b', r'\bmkdir\b']
    for pattern in py_indicators:
        if re.search(pattern, code_content, re.MULTILINE):
            return '.py'
    for pattern in bash_indicators:
        if re.search(pattern, code_content, re.MULTILINE):
            return '.sh'
    return '.py'

def get_code_definitions(code_snippets):
    client = OpenAI(api_key=OPENAI_API)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains code snippets. Strictly describe the functionality of the code in 4-5 lines."},
                {"role": "user", "content": f"Explain what the following code does:\n\n{code_snippets}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
