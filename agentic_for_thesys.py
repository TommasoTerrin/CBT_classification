from langgraph.graph import StateGraph, END
from typing import Dict, Literal, Optional, List
from typing_extensions import TypedDict #for python version before 3.12 (update in the future)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

import prompt as pr
from dotenv import load_dotenv

# Create and show the graph
import networkx as nx


# Define the OpenAI model via Langraph
load_dotenv() # load enviromental variable (for openai)




# ------------------------ OUTPUT DATA MODELS (Pydantic) ---------------------------------------

# ------------------ Pydantic Schema for ER output -----------------
class EROutput(BaseModel):
    """Define the schema for the ER output (First Node)"""
    class Entity(BaseModel):
        id: str
        type: Literal["Situation", "Thought"]
        text: str

    class Relationship(BaseModel):
        from_id: str = Field(alias="from")
        to_id: str = Field(alias="to")
        text: Literal["make me think that"]

    entities: Optional[list[Entity]] # depends on the text if there are or not entities
    relationships: Optional[list[Relationship]] #""""


# -------------------- Pydantic Shema for trplets ----------------------
class Triplet(BaseModel): #triplet model (string specified with Field()
            thought_id: str
            triplet: str= Field(
                description= """the triplet is composed by Situation["text"] + relation["text"] + Thought["text"], 
                The triplets is rewritten in plain english sentence, matching the three-element set of the 'simple triplet'. """
                )            
class TripletsOutput(BaseModel): # List of triplets
    """Define the schema for the output of the second node"""
    triplets: Optional[List[Triplet]]


# ------------------ Pydantic Schema for cognitive distortions -----------------
class DistortionsOutput(BaseModel):
    class Distortion(BaseModel):
            name: Literal["all-or-nothing thinking", "overgeneralization", "mental filter", "mind reading", "fortune-telling", "magnification","emotional reasoning", "should statements", "labeling", "personalization"]
            explanation: str = Field(description= "Brief explanation (one sentence) of why that segment is classified with that distortion based on that narrative.")
    
    distortions: Optional[List[Distortion]]

# ------------------- Define the state model for the graph -------------------
class State(TypedDict):
    input_text: str
    #summary: Optional[str]
    er_schema: Optional[EROutput]
    triplets: Optional[TripletsOutput]
    distortions: Optional[DistortionsOutput] # to be defined better
    dist_list: Optional[List[Literal["all-or-nothing thinking", "overgeneralization", "mental filter", "mind reading", "fortune-telling", "magnification","emotional reasoning", "should statements", "labeling", "personalization"]]]




# ----------------------------------------------------------------------------------------------
# --------------------------- INITIALIZE LLM -------------------------------
# Initialize different LLM objects for diffrent agents

def create_er_llm(temperature=0.2):
    return ChatOpenAI(
        model="gpt-4o",
        temperature= temperature
    ).with_structured_output(EROutput) #force pydantic data structure

def create_triplets_llm(temperature=0.2):
    return ChatOpenAI(
        model="gpt-4o",
        temperature= temperature
    ).with_structured_output(TripletsOutput) #force pydantic data structure

def create_dist_llm(temperature=0.2):
    return ChatOpenAI(
        model="gpt-4o",
        temperature= temperature
    ).with_structured_output(DistortionsOutput) #force pydantic data structure




# ------------------------ GRAPH "DATABASE" --------------------------------------
class GraphDB:
    """
    A class to represent a graph database for storing entities and relationships.

    This class provides methods to initialize a directed graph (DiGraph) from input data,
    add entities and relationships to the graph, extract triplets involving entities of type "Thought",
    and display the graph visually.

    Attributes:
        input_data (EROutput): The input data containing entities and relationships.
        G (networkx.DiGraph): The directed graph to store entities and relationships.
    """
    def __init__ (self, input_data:EROutput):
        self.input_data = input_data
        self.G=nx.DiGraph() # create a new graph db

    def add_elements(self):
        """
        Adds entities and relationships from the input data to the graph "DB" (stored in self.G)

        Returns:
            None
        """
        # Add entities
        for entity in self.input_data.entities:
            node_id = entity.id
            self.G.add_node(node_id, type=entity.type, text=entity.text)
        # Add relationships
        for relation in self.input_data.relationships:
            self.G.add_edge(relation.from_id, relation.to_id, text=relation.text)


    def extract_triplets(self):
        """
        Extracts triplets from the graph where one of the entities is of type "Thought".
        They're going to be used to identify cognitive distortions.

        Returns:
            TripletsOutput: A dictionary with entity IDs of type "Thought" as keys and lists of triplets as values.
        """
        triplets_output= TripletsOutput(triplets=[])
        for u, v in self.G.edges():
            entity_1 = self.G.nodes[u]
            entity_2 = self.G.nodes[v]
            relation = self.G[u][v]

            thought_id = str(u)
            triplet_text= f'"{entity_1["text"]}",  "{relation["text"]}"  "{entity_2["text"]}"'
            triplet= Triplet(thought_id= thought_id, triplet= triplet_text)
            triplets_output.triplets.append(triplet)

        return triplets_output

   


# ----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
##################### MULTI-AGENT GRAPH CREATION ##############################

# --------------------------- NODES DEFINITIONS --------------------------------------------
# Node1: extract ER-schema
def node1 (state: State) -> State:
    llm= create_er_llm()
    prompt= pr.er_prompt2(state["input_text"])
    response= llm.invoke(prompt)
    return {"er_schema": response}

# Node2: extract triplets from the knowledge base
def node2 (state:State) -> State:
    data= state["er_schema"]
    graph_db= GraphDB(data)

    graph_db.add_elements()
    triplets= graph_db.extract_triplets()
    return {"triplets": triplets}

#Node3: analyze the triplets to identify cognitive distorsions
def node3(state:State) -> State:
    dist_name_list=set()
    input_text= str(state["triplets"])
    llm= create_dist_llm()
    dist_list=llm.invoke(pr.distorsions_prompt2(input_text))

    if dist_list.distortions:
        for distorsion in dist_list.distortions:
            dist_name_list.add(distorsion.name)
        
        dist_name_list= list(dist_name_list)
    return {"distortions": dist_list, "dist_list": dist_name_list}
    


# ----------------------------------- CREATE THE MULTI-AGENT GRAPH ------------------------------------
def create_cbt_graph():
    # GRAPH OBJECT CONSTRUCTOR
    builder = StateGraph(State)
    
    # ----------------- ADD NODES ----------------------
    builder.add_node("node1", node1)
    builder.add_node("node2", node2)
    builder.add_node("node3", node3)
    
    # ----------------- ADD EDGES ----------------------
    builder.add_edge("node1", "node2")
    builder.add_edge("node2", "node3")    
    builder.add_edge("node3", END)
    # Set entry point
    builder.set_entry_point("node1") # "start node"
    
    # Compile the graph
    return builder.compile()


# ------------------------- RUN THE GRAPH ----------------------
def run_cbt_graph(thoughts: str, situations: str):
    graph= create_cbt_graph()
    input_text= f" **Thoughts**: {thoughts}\n\n Situations: {situations}"
    result= graph.invoke({"input_text": input_text})
    return result



#-------------- List of distorsion (for the avaluation) ------------------
def list_distortions(s: str, t:str):
    """
    param s: list of situations (from the input dataset)
    param t: list of thoughts (from the input dataset)

    return: list of cognitive distortions
    """
    result= run_cbt_graph(t,s)
    return result["dist_list"]




