from dotenv import load_dotenv
import os

# Load Environment Vars
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set default API key for Agents
from agents import set_default_openai_key
set_default_openai_key(OPENAI_API_KEY)

# Define Search Agent
from agents import Agent, WebSearchTool
search_agent = Agent(
    name = "FitnessSearchAgent",
    instructions=(
        "Immediately call the WebSearchTool to find up-to-date fitness information or trends based on the user's query."
    ),
    tools=[WebSearchTool()]
)

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

from agents import FileSearchTool

# Define Knowledge Agent
def create_vector_store(store_name: str) -> str:
    vs = client.vector_stores.create(name=store_name)
    return vs.id

vs_id = create_vector_store("Fitness Knowledge Base - PMK")
knowledge_agent = Agent(
    name = "FitnessKnowledgeAgent",
    instructions="Answer user questions about Fitness programs with concise, helpful responses using the FileSearchTool.",
    tools=[FileSearchTool(max_num_results=3, vector_store_ids=[vs_id])]
)

# Define custom tool for Account Agent
from agents import function_tool

@function_tool
def get_membership_info(user_id: str) -> dict:
    """Retrun dummy membership data for a given user"""
    return {
      "user_id": user_id,
      "name": "Jane Doe",
      "membership_level": "Platinum",
      "remaining_sessions": 8,
  }
account_agent = Agent(
    name="FitnessAccountAgent",
    instructions="Provide membership information based on a user ID using the get_membership_info tool.",
    tools=[get_membership_info]
)

# Setup Triage Agent
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
triage_agent = Agent(
    name="FitnessAssistant",
    instructions=prompt_with_handoff_instructions(
"""
You are the virtual fitness assistant for FitLife. Welcome the user and ask how you can help.
Based on the user's intent, route to:
- FitnessAccountAgent for membership queries,
- FitnessKnowledgeAgent for workout or nutrition FAQs,
- FitnessSearchAgent for general fitness trends or real-time info.
"""
    ),
    handoffs=[account_agent, knowledge_agent, search_agent]
)

from agents import Runner, trace
import asyncio

async def test_queries():
    examples = [
    #   "What is my remaining session count? My user ID is 12345",
      "Tell me about the Fitness - Why Is Physical Activity So Important?",
    #   "What fitness trends are popular right now?",
    ]
    with trace("FitLife Assistant Test"):
      for query in examples:
          result = await Runner.run(triage_agent, query)
          print(f"User: {query}\n{result.final_output}\n---")

def main():
    asyncio.run(test_queries())


    print("Hello from agent-sdk-lab!")


if __name__ == "__main__":
    main()
