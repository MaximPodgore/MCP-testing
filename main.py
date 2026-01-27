from utils.model import model
from utils.skill_middleware import SkillMiddleware
from utils.tools import curl, load_skill
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import uuid

# agent with our custom model and skill middleware
agent = create_agent(
    model=model,
    system_prompt=(
            "You are a helpful assistant"
        ),
    tools=[curl, load_skill],
    middleware=[SkillMiddleware()],  
    checkpointer=InMemorySaver(),
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