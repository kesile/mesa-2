import openai, os

from agents import agents

api_key = ""
openai.api_key = api_key

agentOne = agents.Agent(api_key, "City Science Researcher named Allen")
agentTwo = agents.Agent(api_key, "AI Researcher named Kessler")

os.system('clear')

def recursive_chat(agent_one, agent_two, subject, rounds):
    if rounds == 0:
        return

    agent_one_dialogue = agent_one.chat(f"Respond to this: {subject}")
    print(agent_one_dialogue)
    print("\n----------------------------------------\n")
    agent_two_dialogue = agent_two.chat(f"Respond to this: {agent_one_dialogue}")
    print(agent_two_dialogue)
    print("\n----------------------------------------\n")


    recursive_chat(agent_one, agent_two, agent_two_dialogue, rounds - 1)


recursive_chat(agentOne, agentTwo, "The impact of AGI on the economy.", 15)