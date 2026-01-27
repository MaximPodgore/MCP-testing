# UCSD Agent testing

## Current Architecture

Langchain agent with tools and skill middleware. The middleware looks at the request, identifies if any skills is relevant, and then loads the skill definition into context for the agent. Then the agent can call tools using the task and loaded skill definitions as context

Current tools:
- `curl`: As named
- `load-skill`: As named, but isn't currently called because the middleware bypasses it.

## TODO
- Determine how exactly I want skills/tools to interact 

## Setup
Conda environment for clean local dev environments


```
conda create -n "agents_ucsd" python==3.10
conda activate agents_ucsd
pip install -r requirements.txt
python main.py
```