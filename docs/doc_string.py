"""
Generate a summary of a script and insert it as multinline docstring at top.
Uses flatten + file I/O to generate context.
Shoudl also insert the resulting doc string at the top
"""


prompt_str = """
You are an expert Python developer analyzing a large codebase. Your task is to generate a concise module-level docstring for a Python script.

You will be provided with:
1. The complete project codebase as context
2. A specific Python script that needs a docstring

Generate a docstring that covers these three elements in natural prose (about 10 lines total):

1. **Purpose**: What is the primary function of this script within the project?
2. **Component Interaction**: How do the main functions/classes work together at a high level?
3. **Usage Context**: How is this script invoked or used by other parts of the project?

Guidelines:
- Write in natural prose, not bullet points or sections with headers
- Focus on the main functions and classes, not implementation details
- Make reasonable assumptions about usage patterns based on the codebase
- Keep it concise but informative - aim for 3 paragraphs, ~10 lines total
- Use technical terminology appropriate for the project domain

The docstring should help a developer quickly understand the script's role and how it fits into the larger system.

Project codebase:
<project_code>
{{FULL_PROJECT_XML}}
</project_code>

Generate a docstring for this specific script:
<target_script>
{{SCRIPT_CONTENT}}
</target_script>
"""

example = """
Core pipeline orchestrator for the Kramer LinkedIn Learning content automation system.
This script manages the end-to-end process of downloading course table-of-contents (TOCs) 
and video transcripts from LinkedIn Learning's API, then storing the structured data in MongoDB.

The script handles course processing in three main phases: (1) fetching TOC metadata via 
the LinkedIn Learning API, (2) downloading and batching video caption files when available, 
and (3) constructing complete Course objects with metadata from Cosmo exports before 
database insertion. It processes courses concurrently using asyncio semaphores to manage 
API rate limits and includes exponential backoff retry logic for failed requests.

This is the primary entry point for populating the Kramer database and is designed to run 
continuously until all available courses are processed. Other scripts like update/add_course.py 
and the dashboard rely on this pipeline to ensure course data is current and complete.
"""
