from langchain.agents.middleware import ModelRequest, ModelResponse, AgentMiddleware
from langchain.messages import SystemMessage, HumanMessage
from typing import Callable
import json

from utils.skill import SKILLS
from utils.model import model




class SkillMiddleware(AgentMiddleware):  
    """Middleware that automatically loads relevant skills based on user requests."""
    
    def __init__(self):
        """Initialize and generate the skills prompt from SKILLS."""
        # Build skills prompt from the SKILLS list
        skills_list = []
        for skill in SKILLS:
            skills_list.append(
                f"- **{skill['name']}**: {skill['description']}"
            )
        self.skills_prompt = "\n".join(skills_list)

    def _get_user_message(self, request: ModelRequest) -> str:
        """Extract the latest user message content."""
        for message in reversed(request.messages):
            # Handle dict-based messages
            if isinstance(message, dict):
                if message.get('role') == 'user' or message.get('type') == 'human':
                    content = message.get('content')
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                return block.get('text', '')
            # Handle message objects
            elif hasattr(message, 'role') and message.role == 'user':
                if isinstance(message.content, str):
                    return message.content
                elif isinstance(message.content, list):
                    for block in message.content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            return block.get('text', '')
            # Handle HumanMessage objects
            elif hasattr(message, 'type') and message.type == 'human':
                if isinstance(message.content, str):
                    return message.content
        return ""

    def _find_relevant_skills(self, user_message: str) -> list[str]:
        """Use LLM to intelligently identify which skills are relevant."""
        skills_list_text = "\n".join([
            f"- {skill['name']}: {skill['description']}"
            for skill in SKILLS
        ])
        
        prompt = f"""Given the following user request and available skills, determine which skills are relevant.

            Available Skills:
            {skills_list_text}

            User Request:
            {user_message}

            Return ONLY a JSON object with a "relevant_skills" key containing a list of skill names (e.g., ["get-weather"]), or an empty list if no skills are relevant.
            Example: {{"relevant_skills": ["get-weather"]}}"""
        
        try:
            response = model.invoke([HumanMessage(content=prompt)])
            # Parse the JSON response
            response_text = response.content.strip()
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            relevant = result.get("relevant_skills", [])
            # Validate that returned skills exist
            valid_skill_names = {s['name'] for s in SKILLS}
            return [s for s in relevant if s in valid_skill_names]
        except Exception as e:
            # If LLM call fails, fall back to empty list
            print(f"Error determining relevant skills: {e}")
            return []

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject skills and pre-loaded skill content into system prompt."""
        # Extract user message and find relevant skills
        user_message = self._get_user_message(request)
        relevant_skills = self._find_relevant_skills(user_message)

        skills_addendum = ""
        # If relevant skills found, add their full content
        if relevant_skills:
            skills_addendum += "\n\n## Relevant Skill Details\n\n"
            for skill_name in relevant_skills:
                for skill in SKILLS:
                    if skill['name'] == skill_name:
                        skills_addendum += f"### {skill_name}\n{skill['content']}\n\n"
                        break


        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)