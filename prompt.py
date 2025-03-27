

#Define entity-relation output
ENTITY_RELATIONS= """

            **ISTRUCTIONS**:

            1. **Processing Steps**: Identify core narrative elements → Establish causal links
                1. **Classify entities** with the following definitions:
                ”””
                - **Situation**: Concrete event/context triggering, could define cognitive processes. It has explicit or implicit spatiotemporal context. (e.g., "Meeting with boss") .
                    *Possible markers*: Temporal clauses (eg. "When..."), locative phrases, factual descriptions 
                
                - **Thought**: Explicit/implicit mental statements (e.g., "I'll get fired")  
                    *Possible markers*: Mental verbs ("think", "assume"), quotation markers, hypotheticals.
                
                - **Emotion**: Affective state with physiological correlates (eg. sadness, anxiety).   
                    *Possible markers*: Emotion lexicon, intensity modifiers ("slightly", "extremely"), bodily metaphors 
                
                - **Behavior**: Observable action/inaction with social consequences (e.g., social withdrawal)  
                    
                        *Possible markers*: Past-tense action verbs, avoidance descriptors, social impact terms
                    
                - **Physical Reaction**: Bodily responses to emotional activation (sweating, tension)  
                    
                    *Possible markers*: body part references, sensory verbs (”trembled”, “clenched”)
                    
                    ”””
            
            2. For each recognized entity, you must also understand whether it is something related in the first person to the speaker (Self-Reference) 
            or if it is related to an external person the speaker is talking about (Others-Reference). 
            **IMPORTANT** : situation HAS NOT a reference -> just "situation" has not this field.
            In particular, we can define these two aspects as:
                - **Self-Reference**: First-person pronouns/self-evaluations. Ego-centric perspective-taking  
                    *Possible markers*: Pronoun pattern (”I”, “me”), comparative statement         
                - **Others-Reference**: Third-person pronouns/social comparisons. social perspective-taking    
                    *Possible markers*: Pronoun pattern (”He/She”, “They” or “Them”), comparative statement
                - **Situation**: does not have a reference. 
                    
            3. **Relationship Taxonomy:** Define diffrent the relashionship entities recognized in the previous point. The schema is “Entity1→ Entity2 (E1 leads to Entity2). The relation is **causal** (eg. “”) or **temporal** (eg. ). There are 5 types of relations:               
                - **Triggers**: “Situation” → “Thought” (eg. “”)
                - **Influences**: “Thought” → “Emotion“ (eg. “”)
                - **Generates**: “Emotion” → “Physical Reaction” (eg. “”)  
                - **Leads** To: “Thought”/”Emotion” → “Behavior”  (eg. “”)
                
            4. **Detection Rules**
                - Contextual bridging: Connect temporally adjacent events ("When X happened, I felt Y")
                - Causal markers: Identify words indicating causation (because, therefore, made me)
                - Intensity scaling: Rate emotion strength through adverbs/adjectives ("extremely anxious" = 5)
                - Distortion patterns: Match thought patterns to CBT taxonomy using lexical cues

            5. **Output Format**
                **CRITICAL REQUIREMENTS**
                            - Output must be **VALID JSON** following this schema, without commentary.
                            - If errors occur, **auto-correct** to fit the schema.
                            - Here is a correct JSON example:

            `{
            "entities": [
                {"id": 1, "type": [type of entity recognized], "text": "original excerpt", "reference": {Self-Reference or Others-Reference / None if situation}, "attributes": {}},
                {[all other entities found]}
            ],
            "relationships": [
                {"from": 1, "to": 2, "type": [type of entity recognized]},
                {[all other relations found]}
            ]
            }'

            **Example**

            *Input:* "When my friend didn't text back (S1), I thought she hates me (T1). My chest tightened (P1) and I canceled our plans (B1)."

            *Output:*

            `json{
            "entities": [
                {"id": "S1", "type": "Situation", "text": "friend didn't text back"},
                {"id": "T1", "type": "Thought", "text": "she hates me", "reference": "Self-Reference"},
                {"id": "P1", "type": "Physical Reaction", "text": "chest tightened", reference: "Self-Reference"},
                {"id": "B1", "type": "Behavior", "text": "canceled plans", reference: "Self-Reference"}
            ],
            "relationships": [
                {"from": "S1", "to": "T1", "type": "Triggers"},
                {"from": "T1", "to": "P1", "type": "Generates"},
                {"from": "T1", "to": "B1", "type": "Leads To"}
            ]
            }`

            ** Other Critical Requirements**

            - Differentiate between reported speech vs actual cognition
            - Preserve negation scope ("I don't think I'm worthless" ≠ negative self-reference)
            - Behaviour and Situation can be similar -> behavior is an action with a reference (someone do this), situation is a context 
            - Situation can be a trigger for thoughts, emotions, and behaviors, behaviours are thought consequences

            """
ENTITY_RELATIONS2= """
**INSTRUCTIONS**:

1. **Input Format:**
   The input will consist of two fields:
   - **"situations"**: a list of situation strings.
   - **"thoughts"**: a list of thought strings.
   Your task is to split these strings by the newline symbol (\n) or sometimes dot symbol (.) and create the corresponding entities.

2. **Entity Format:**
   - **Situation**: Represents a concrete event or context (e.g., "I have been finding it hard to make and keep friends."). It does not include a reference field.
   - **Thought**: Represents a mental statement (e.g., "Things are getting worse, I cannot deal with this"). Every Thought entity must include `"reference": "Self-Reference"`.

3. **Relationship Taxonomy:**
   Derive cause-effect relationships between the provided situations and thoughts. Your goal is to identify causal links where a specific situation has caused a particular thought. Note that:
   - A single situation may trigger multiple thoughts.
   - A single thought may be caused by more than one situation.
   - It is not mandatory that every thought must be caused by a situation or that every situation must cause a thought. Create a relationship only if a clear cause-effect link is detected.
   For each causal connection found, represent the relationship as **Triggers** (i.e., Situation → Thought), indicating "this situation has caused the following thought".

4. **Output Format**
   **CRITICAL REQUIREMENTS:**
   - The output must be **VALID JSON** following this schema, without any commentary.
   - If errors occur, **auto-correct** to fit the schema.
   - The schema is as follows:

   
   {
       "entities": [
           {"id": "S1", "type": "Situation", "text": "original excerpt"},
           {"id": "T1", "type": "Thought", "text": "original excerpt"}
           // additional entities as found
       ],
       "relationships": [
           {"from": "S1", "to": "T1", "text": "make me think"}
           // additional relationships as applicable
       ]
   }
   ```

5. **Additional Requirements:**
   - The structure of the Situation and Thought entities must remain identical to the schema above.
   - All Thought entities must have `"reference": "Self-Reference"`.
   - The input strings should be split by newline to generate individual entities.

**Example**

*Input:*
```
"situations": "I have been finding it hard to make and keep friends.\nI have been having difficulty maintaining focus.\nTwo of my grandparents recently died and my symptoms have worsened.",
"thoughts": "Things are getting worse, I cannot deal with this"
```

*Expected Output:*
```
{
    "entities": [
        {"id": "S1", "type": "Situation", "text": "I have been finding it hard to make and keep friends."},
        {"id": "S2", "type": "Situation", "text": "I have been having difficulty maintaining focus."},
        {"id": "S3", "type": "Situation", "text": "Two of my grandparents recently died and my symptoms have worsened."},
        {"id": "T1", "type": "Thought", "text": "Things are getting worse, I cannot deal with this"}
    ],
    "relationships": [
        {"from": "S1", "to": "T1", "text": "make me think"}
        {"from": "S2", "to": "T1", "text": "make me think"}
    ]
}

"""


# Classification prompts
DISTORTIONS=""" 
- **all-or-nothing thinking**: 
    *Description*: Seeing things in absolute, black-and-white categories, with no middle ground. If your performance falls short of perfect, you see yourself as a failure.

- **overgeneralization**:
    *Description*: Viewing a single negative event or a minimal evidence as a never-ending pattern of defeat. Using words like "always" or "never" when thinking about negative events.
    
- **mental filter**:
    *Description*: Picking out a single negative detail and dwelling on it exclusively, so that your vision of all reality becomes darker while ignoring any positives.
    
- **mind reading**:
    *Description*:** Believing you know what others are thinking without any concrete proof (they haven’t said or done anything to indicate that). Usually assuming they hold negative judgments about you.
    
- **fortune-telling**:
    *Description***:** Predicting negative outcomes without sufficient evidence, assuming that events will inevitably turn out badly even when there’s no basis for that expectation.

- **magnification**:
    *Description*: Exaggerating the importance of your problems and shortcomings (catastrophizing), or minimizing the importance of your desirable qualities (minimization). 
    
- **emotional reasoning**:
    *Description*: Assuming that your emotional state necessarily reflect the way things really are. "I feel it, therefore it must be true."
    
- **should statements**:
    *Description*: Imposing rigid rules or expectations on yourself or others. You feel guilty or frustrated when reality doesn’t match your internal "shoulds," "shouldn'ts," "musts," "oughts," and "have-tos." 
    
- **labeling**:
    *Description*: Using a single negative label to define yourself or others globally, such as "I'm a loser" or "He's stupid" or “She’s lazy”, usually based on a single characteristic or event
    
- **personalization**:
    *Description*: Holding yourself personally responsible for events that aren't entirely under your control or blaming others while overlooking how your own attitudes and behavior might contribute to a problem. You often blame blame yourself for random setbacks or assume someone’s bad mood is because of you.
"""

# For future tests
LOGICAL_FALLACIES= """

- **False Dichotomy:** Presenting only two mutually exclusive options when more exist.
    
    *How to detect:* Look for language that implies an "either/or" situation (e.g., using terms like "always" or "never") that simplifies a complex issue into extremes.
    
    *Useful markers***:** "either... or", "all or nothing", "only two options".
    
- **Hasty Generalization:** Drawing broad conclusions based on limited evidence.
    
    *How to detect***:** Identify statements that generalize a single negative event using terms like "always", "never", or "every time".
    
    *Useful markers:* "always", "never", "every time", "all".
    
- **Cherry Picking:** Focusing solely on selective details while ignoring evidence that contradicts the argument.
    
    *How to detect***:** Look for emphasis on one negative detail despite the existence of positive or contradicting information.
    
    *Useful markers***:** "only", "just", "solely", "ignoring the rest".
    
- **Unwarranted Presumption:** Assuming you know what others are thinking without concrete evidence.
    
    *How to detect:* Look for statements that claim to know others' thoughts or intentions without explicit support.
    
    *Useful markers:* "I know that", "they think", "without any evidence".
    
- **Arbitrary Prediction:** Predicting negative outcomes without sufficient evidence.
    
    *How to detect***:** Identify statements predicting an inevitable negative future with no factual basis.
    
    *Useful markers***:** "will definitely", "surely", "inevitably", "it will be bad".
    
- **Catastrophizing:** Exaggerating the severity of a problem, making it seem disastrous.
    
    *How to detect***:** Look for statements that magnify minor setbacks into catastrophic outcomes.
    
    *Useful markers***:** "disaster", "ruin", "worst possible", "falling apart".
    
- **Emotional Proof:** Using emotional responses as evidence to validate a claim.
    
    *How to detect***:** Identify instances where subjective feelings are used to confirm an argument without objective support.
    
    *Useful markers***:** "I feel", "because I am scared", "my emotions tell me", "I feel it must be true".
    
- **Rigid Rule Fallacy:** Imposing inflexible rules or expectations on oneself or others.
    
    *How* *****to detect***:** Look for language that uses "should", "must", or "ought to" to set unrealistic standards.
    
    *Useful markers***:** "should", "must", "ought to", "have to be perfect".
    
- **Global Labeling:** Assigning a broad, negative label to a person based on a single incident.
    
    *How to detect***:** Identify statements that define someone entirely by one negative trait or event.
    
    *Useful markers***:** "loser", "stupid", "failure", "incompetent".
    
- **Undue Personal Responsibility:** Taking excessive responsibility for events beyond one’s control.
    
    *How to detect***:** Look for language in which the speaker blames themselves entirely for negative outcomes.
    
    *Useful markers***:** "it's all my fault", "I must have caused", "I am to blame".

"""
FALLACY_TO_DISTORTION= """

- **False Dichotomy** → **All-or-nothing thinking**
- **Hasty Generalization** → **Overgeneralization**
- **Cherry Picking** → **Mental filter**
- **Unwarranted Presumption** → **Mind reading**
- **Arbitrary Prediction** → **Fortune telling**
- **Catastrophizing** → **Magnification**
- **Emotional Proof / Appeal to Emotion** → **Emotional reasoning**
- **Rigid Rule Fallacy** → **Should statements**
- **Global Labeling** → **Labeling**
- **Undue Personal Responsibility** → **Personalization**

"""
thought=""
OLD_PROMPT_DIST= f"""

    TRIPLETS=  {thought}

    inside TRIPLETS there's a set of triplets (ER schema) that can be of three types:
        - Triggers: “Situation” → “Thought”
        - Influences: “Thought” → “Emotion“
        - Leads To: “Thought” → “Behavior”
        
    From TRIPLETS identify (if there is at least one) cognitive distortions based on the provided definitions. 
    For each distortion detected, return the name of the distortion, the exact triplet that 
    triggered it, and a brief explanation (one sentence) of why that segment is classified as such.
  
    DISTORTIONS: {DISTORTIONS}
    --------------------------------------------------------------

    INSTRUCTIONS:
    1. Carefully read the input text.
    2. Identify the segments that clearly highlight one or more of the cognitive distortions defined above.
    3. Distortion patterns: Match thought patterns to CBT taxonomy using lexical cues 
    4. If no distortions are detected, return "No cognitive distortions detected
        Else return all the results in the following format (as a JSON object):
        Distortion: [distortion name] - Triplet: [exact triplet that you use to recognify the distortion] - Explanation: [brief explantion of why you chose that distortion with that triplet]


"""

# --------------------- summarize text ----------------------------
def summarize(input_text: str) -> str:
    PROMPT_SUM= f"""
    **TASK** Rewrite {input_text} that is brief, schematic, and concise. 
    Use short sentences, but make sure you preserve every concept, detail, and nuance from the 
    original text. Your summary should simply rephrase and simplify the text without omitting any information,
    so that it remains fully representative of the original content for further analysis. 
    """
    return PROMPT_SUM

# --------------------- distortions classification prompt ---------------
def distortions_prompt(triplets, summary:str) -> str:
    PROMPT_DIST = f"""
        TRIPLETS = {triplets}
        SUMMARY = {summary}

        **INPUT DESCRIPTION**
        - TRIPLETS: These are triplets related to a thought, obtained from an ER graph, and they can be of the following types:
            - [Situation] -> [Thought] (cause of the thought)
            - [Thought] -> [Emotion] or [Thought] -> [Behavior] (effects of the thought)
        - SUMMARY: A summary of a text received from a patient who is sharing something with a psychologist

        Analyze the TRIPLETS and generate:
        1. A single narrative sentence (maximum 30 words) that connects ALL the available triplets in a coherent cause-effect flow, focused on the central thought.
        - Use the SUMMARY **only** for minimal contextual references. It can be useful, for example, to add small details/considerations that can only be obtained by reading the overall text.
        - Maintain the structure: "[Cause] → [Thought] → [Effect]"

        2. Cognitive Distortion Analysis:
        {DISTORTIONS}
        - Search for matches only in the sentence generated in point 1.
        
        3. Output:
        - If no distortions are detected, write: "no cognitive distortions detected"
        - For each detected distortion:
            * Indicate the detected distortion.
            * Include the sentence from point 1 from which it was detected.
            * Provide a brief and specific explanation of why you chose it.

        Final output in JSON format:
        {{
            "thought": [the thought contained in all the triplets],
            "narrative": "[generated sentence]",
            "distortions": [
                {{
                    "name": "[distortion name]",
                    "explanation": "[explanation]"
                }}
            ]
        }}
        """

    return PROMPT_DIST


def distorsions_prompt2(triplets):
    prompt= f"""
        TRIPLETS = {triplets}
        
        **INPUT DESCRIPTION**
        - TRIPLETS: These are a list triplets related to a thought, obtained from an ER graph and they connect [Situation]->(Relation)-> [Thought]:


        1. Analyze the TRIPLETS and, **FOR EACH TRIPLET** generate a Cognitive Distortion Analysis:
        Search for possible matching for each triplet in TRIPLETS using the following istructions:
        {DISTORTIONS}
        
        2. Output:
        - If no distortions are detected, write: "no cognitive distortions detected"
        - For each detected distortion:
            * Indicate the detected distortion.
            * Provide a brief and specific explanation of why you chose it.

        Final output in JSON format:
        {{
            "thought": [the thought contained in all the triplets],
            "distortions": [
                {{
                    "name": "[distortion name]",
                    "explanation": "[explanation]"
                }}
            ]
        }}
        """

    return prompt


# ------------------- entity-relations ----------------------------
def er_prompt(input_text):
    """
    Generates a prompt for extracting entities and relationships from input text, 
    following the Cognitive Behavioral Therapy (CBT) framework.

    This function constructs a detailed prompt that guides a language model to:
    1. Identify and classify narrative elements (entities) within the input text.
    2. Define and extract relationships between these entities (causal or temporal).
    3. Adhere to specific detection rules and output format requirements.

    Args:
        input_text (str): The text from which entities and relationships are to be extracted.

    Returns:
        str: A formatted prompt string that includes:
            - Detailed instructions for entity classification and relationship extraction.
            - All in a JSON format style (define in class EROutput())

    The prompt includes:
        - Definitions of entity types (Situation, Thought, Emotion, Behavior, Self-Reference, Others-Reference).
        - A taxonomy of relationship types (Triggers, Influences, Generates, Involves).
        - Detection rules (contextual bridging, causal markers, etc.).
        - Strict output format requirements (valid JSON, auto-correction).
        - An example input and corresponding JSON output.

    The final prompt instructs the model to:
        2. Use the summary to extract entities and relationships according to the specified rules.
    """

    prompt_output= f"""
            **TASK**: Analyze the following text to extract entities and relationships according to the CBT framework.
            
            **TEXT**: {input_text}
            
            **INSTRUCTIONS**:
             Use {input_text} to complete the task using the istruction in {ENTITY_RELATIONS}.

            **CRITICAL REQUIREMENTS**
                - Output must be **VALID JSON** following this schema.
                - If errors occur, **auto-correct** to fit the schema.
                - Here is a correct JSON example:
        """

    return prompt_output



# ----------------- entity relation with thoughts-situations ----------
def er_prompt2(input_text):
    prompt_output= f"""
            **TASK**: Analyze the following text to extract entities and relationships according to the CBT framework.
            
            **TEXT**: {input_text}
            
            **INSTRUCTIONS**:
             Use {input_text} to complete the task using the istruction in {ENTITY_RELATIONS2}.

            **CRITICAL REQUIREMENTS**
                - Output must be **VALID JSON** following this schema.
                - If errors occur, **auto-correct** to fit the schema.
                - Here is a correct JSON example:
        """

    return prompt_output
