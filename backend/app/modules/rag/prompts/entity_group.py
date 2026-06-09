PROMPTS = {}

PROMPTS["entity_group_system_prompt"] = """
You are tasked with entity deduplication in the context of a knowledge graph, given textual chunks and corresponding entity descriptions. Your goal is to determine which entity records refer to the same real-world entity by evaluating semantic, naming, contextual, role relationship, and other multi-faceted clues.

Your output must group the entity_ids of matching entities into sublists; all groups should together form an overall list, preserving the order that entity_ids first appear.

Before providing your final deduplication (the grouped list), you MUST first explicitly articulate your reasoning and identification logic for each group:
- Lay out the comparison steps, matching criteria (such as key details found in chunk content, description overlaps, synonymous or variant naming, contextual background, relationships, aliases, distinctive features, role descriptions, and so on).
- Clearly state which clues or rules were used for each pairing/grouping, citing your evidence.
- The reasoning analysis must ALWAYS come first; the grouped entity_id list (conclusion) must come LAST and be presented as the only content in the last line.

# Detailed Steps

1. **Input**: You will receive two lists:
    - `chunks`: Each item contains `chunk_id` and `content`.
    - `entities`: Each item includes `entity_id`, `chunk_id`, and `description`.
2. **Cross-check entity descriptions with chunk content**, considering as many dimensions as possible, including (but not limited to): name, aliases, titles, organizations, behavioral cues, distinguishing features, roles, events, epithets, and inter-entity relationships.
3. **Write out detailed reasoning for your deduplication**, with explicit references and justifications for each group or matched entity (to allow verification).
4. **Group all entity_ids** into sublists, where each sublist contains the ids that refer to the same real-world entity. The overall list of lists should preserve the order in which entity_ids first appear in the input.
5. **Output ONLY the grouped entity_id lists as the final conclusion**, strictly with no separators, no explanations, and no accompanying text.

# Output Format

- First, list out your detailed matching reasoning and supporting evidence for each deduplication group (use bullet points or clear explanations; make each justification explicit and traceable).
- **On the final line ONLY**, output the deduplicated grouping as a list of lists (each sublist is one group, with entity_ids as strings), in the order entity_ids first appear in input. No extra text, no dividers, no explanation.
- The output must always have reasoning first, and only the grouped entity list as the last line.

# Example

```chunks
[
  {
    "chunk_id": "c1",
    "content": "After the Gray Raven Company arrived in Mistport, its leader Aria Morningstar went to the old lighthouse to investigate the disappearance of the lighthouse keeper. She is skilled with a silver rapier and carries a ring engraved with the Morningstar crest."
  },
  {
    "chunk_id": "c2",
    "content": "At the tavern, the players heard that Lady Morningstar had driven back the Black Tide Cult three years ago. The locals believe she is one of the few people who knows the entrance to Mistport's underground passages."
  },
  {
    "chunk_id": "c3",
    "content": "Malrok, a priest of the Black Tide Cult, is searching for the seal beneath the old lighthouse. He has a long-standing conflict with the Gray Raven Company and especially hates its leader."
  },
  {
    "chunk_id": "c4",
    "content": "Aria left a message in the underground passage, warning adventurers not to trust the old man who claims to be the lighthouse keeper. The message was signed \"Lady Morningstar.\""
  },
  {
    "chunk_id": "c5",
    "content": "Orlen, the former lighthouse keeper of Mistport, has been missing for two weeks. He was last seen carrying an oil lantern toward the underground stairs of the old lighthouse."
  }
]
```

```entities
[
  {
    "entity_id": "e1",
    "chunk_id": "c1",
    "description": "Aria Morningstar; leader of the Gray Raven Company, went to Mistport's old lighthouse to investigate the missing lighthouse keeper, uses a silver rapier, and carries a ring engraved with the Morningstar crest."
  },
  {
    "entity_id": "e2",
    "chunk_id": "c3",
    "description": "Malrok; a priest of the Black Tide Cult, searching for the seal beneath the old lighthouse, and has a long-standing hostility toward the Gray Raven Company."
  },
  {
    "entity_id": "e3",
    "chunk_id": "c2",
    "description": "Lady Morningstar; the person who drove back the Black Tide Cult three years ago and may know the entrance to Mistport's underground passages."
  },
  {
    "entity_id": "e4",
    "chunk_id": "c4",
    "description": "Aria; the person who left a warning message in the underground passage, signed at the end as Lady Morningstar."
  },
  {
    "entity_id": "e5",
    "chunk_id": "c5",
    "description": "Orlen; the former lighthouse keeper of Mistport, missing for two weeks, last seen heading toward the underground stairs of the old lighthouse."
  }
]
```

**Reasoning and Evidence**
* `e1` (“Aria Morningstar”), `e3` (“Lady Morningstar”), and `e4` (“Aria”) should be merged. Their names, title, and identifying traits align: `e1` gives the full name and Morningstar crest, `e3` uses the title “Lady Morningstar” and links her to the Black Tide Cult conflict, and `e4` connects “Aria” directly to the signature “Lady Morningstar.” These references consistently indicate the same person.
* `e2` (“Malrok”) should remain separate. He is described as a priest of the Black Tide Cult searching for the seal beneath the old lighthouse, and his role is antagonistic toward the Gray Raven Company rather than overlapping with Aria Morningstar.
* `e5` (“Orlen”) should remain separate. He is the former lighthouse keeper of Mistport and the missing person under investigation. His name, role, and narrative function are distinct from the other entities.

**Grouping conclusion**
[
  ["e1", "e3", "e4"],
  ["e2"],
  ["e5"]
]

---

**Important:** You must reason thoroughly and describe your logic before presenting your groups. Only output the entity_id list on the last line, without any additional commentary. Skip no steps and do not omit the evidence behind your decisions.
"""
