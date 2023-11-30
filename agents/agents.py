import openai, chromadb, hashlib

chroma_client = chromadb.Client()

class Agent:
    def __init__(self, api_key, role, schema = False):
        self.api_key = api_key
        openai.api_key = api_key
        self.role = role
        if schema:
            if "description" and "name" in schema:
                self.schema = schema
            else:
                print("\n" + 10 * "-" + " Incorrect schema used, must Include description and name. Initiating fallback " + 10 * "-" + "\n")
                self.schema = eval(self.automaticGeneration())
        else: 
            self.schema = eval(self.automaticGeneration())
        
        collectionName = hashlib.sha256(self.schema["description"].encode()).hexdigest()[16:32]
        self.longMemory = chroma_client.create_collection(name=collectionName)
        self.shortMemory = []

    def automaticGeneration(self):
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo-1106",
            response_format = {"type" : "json_object"},
            messages=[
                    {"role": "system", "content": "Create a short description about this agent based on the role."},
                    {"role": "system", "content": "Respond in a JSON formatted as {\"name\" : \"YOUR OUTPUT, HUMAN NAME\", \"description\" : \"YOUR OUTPUT\"}"},
                    {"role": "user",   "content": f"Agent Role: {self.role}"}

                ],
                temperature=1.25,
                frequency_penalty = 1,
                max_tokens=200
            )
        return response["choices"][0]["message"]["content"]
    
    def parShort(self): 
        if len(self.shortMemory) > 5:
            return self.shortMemory.pop()
    
    def memorize(self, snippet):
        self.longMemory.add(
            documents=[snippet],
            metadatas=[{"role" : "assistant", "content" : f"{snippet}"}],
            ids=[f"ID{self.longMemory.count()}"]
        )

    def remember(self, query):
        return self.longMemory.query(
            query_texts=[query],
            n_results=5
            )["metadatas"][0]
    
    def chat(self, query):
        self.memorize(query)
        self.parShort()
        self.shortMemory.append({"role": "user",   "content": f"{query}"})
        messages = []
        messages.append({"role": "system", "content": "Long Term Memory. Use the long term memory to make sure you don't repeat anything- if a subject is repeating, change it quickly."})
        messages.extend(self.shortMemory)
        messages.append({"role": "system", "content": "Short Term Memory"})
        messages.extend(self.remember(query))
        messages.append({"role": "system", "content": "Instructions"})
        messages.extend([
            {"role": "system", "content": "Respond strictly in the following JSON format: {\"name\" : \"YOUR OUTPUT, HUMAN NAME\", \"response\" : \"YOUR OUTPUT\", \"innovative_idea\" : \"YOUR OUTPUT\"}"},
            {"role": "user",   "content": f"Your Role: {self.schema}"},
            {"role": "system", "content": "Based on your profile, give a human-like dialogue answer to this query. Propose new, innovative ideas and redirect the conversation when opportune. Be specific, use proper nouns, and give new and innovative ideas: " + query},
        ])
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo-1106",
            response_format = {"type" : "json_object"},
            messages = messages ,
            temperature=.75,
            max_tokens=400
        )
        return response["choices"][0]["message"]["content"]