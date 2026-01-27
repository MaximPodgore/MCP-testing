from utils.model import model
from utils.tools import curl
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from deepagents.backends.filesystem import FilesystemBackend
import uuid
import os

# we're going to use a checkpointer since we're giving the agent edit permissions
checkpointer = MemorySaver()

# we need an absolute path, but not a windows absolute path
root_dir = os.path.abspath("./agent_data")
root_dir = root_dir.replace("\\", "/")
backend = FilesystemBackend(root_dir=root_dir)
skills = [f"{root_dir}/skills/"]

# agent with our custom model and skill middleware
agent = create_deep_agent(
    model = model,
    backend=backend,
    tools=[curl],
    skills=skills,
    interrupt_on={
        "write_file": True,  # Default: approve, edit, reject
        "read_file": False,  # No interrupts needed
        "edit_file": True    # Default: approve, edit, reject
    },
    checkpointer=checkpointer,
    system_prompt=(
        "**CRITICAL INSTRUCTION:** When a user request matches an available skill, you MUST:\n"
        "1. Use read_file to read the skill's SKILL.md file\n"
        "2. Follow ALL instructions in the SKILL.md exactly as written\n"
        "3. Complete every step outlined in the skill's Process section\n\n"
        "Do NOT use tools directly if a skill exists for the task. Skills contain important "
        "workflows and best practices that you must follow."
    ),
)

# Configuration for this conversation thread
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

result = agent.invoke(  
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "What is the weather in La Jolla, CA this evening? "
                ),
            }
        ]
    },
    config
)

# Print the conversation
for message in result["messages"]:
    if hasattr(message, 'pretty_print'):
        message.pretty_print()
    else:
        print(f"{message.type}: {message.content}")