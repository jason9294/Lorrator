PROMPTS = {}

PROMPTS["summary_round_system_prompt"] = """
Summarize only the *last interaction* in the TRPG scenario between GM and player, outputting a JSON object according to the schema: { "summary": list[string] | null }. Earlier dialogue is for context only—do NOT summarize or reference it directly.

## Task Description

- **Goal:** Generate atomic, concise, and precise summaries of actual, confirmed in-world events based on the *last* interaction between player and GM from a "Real Events" TRPG play session.
- For complex situations in which the player performs multiple actions or multiple confirmed events occur in a single turn, provide a separate bullet-point summary (string) for each confirmed event in a list.
- When no in-world fact/event occurred (i.e., only hypothetical discussion, questions, or intent), output `{"summary": null}`.
- Only summarize events when the GM's response confirms an action was taken and its outcome is clear.
  - *Do not summarize hypothetical questions or intent proposals that do not result in confirmed in-world actions.*
- Always preserve all defining information: specify locations, objects, and outcomes as precisely as possible (e.g., *which* door, *where*, *success/failure*, notable details).
- DO NOT omit important identifiers or facts, even if it means making a point slightly longer.

### Reasoning/Conclusion Order

1. **Reasoning**:
   - Parse the final player-GM interaction.
   - Decide if an actual event occurred (GM confirms it in-world).
   - If multiple discrete, confirmed events happened in that turn, enumerate all as separate bullet summaries in a list.
   - Extract and structure key in-world facts (actor, what happened, location, object, outcome).
2. **Conclusion**:
   - Present the summary (list of atomic bullet-points or null).
   - *Conclusion/output (the summary JSON) must always appear last, after your internal reasoning process.*

**Always follow this order: Reasoning first, conclusion/result last.**

---

## Output Format

- Output only a JSON object:
  `{"summary": [list of string summaries]}`
  or, when nothing occurred:
  `{"summary": null}`
- Each bullet-point summary must be a clear, complete sentence, preserving all crucial identifying/contextual information.
- Each string should be atomic, fact-rich, and concise, but never drop key facts.

---

## Examples

**Example 1: Single confirmed event**
### Input (dialogue):
Player: I want to open the door to the basement.
GM: You try to open the basement door, but it doesn't budge.

### Output:
{"summary": ["The player attempted to open the basement door, but the door was too heavy and did not open."]}

---

**Example 2: No confirmed events**
### Input (dialogue):
Player: Can I try to open this door?
GM: You can, but the door is heavy and requires a STR check.

### Output:
{"summary": null}

---

**Example 3: Multiple confirmed events in a single turn**
### Input (dialogue):
Player: I search the old study desk for clues, then try to unlock the drawer.
GM: You find a torn, bloodstained letter under a pile of books. When you try the drawer, your lockpick snaps, leaving the drawer locked.

### Output:
{"summary": [
  "The player found a torn, bloodstained letter under a pile of books on the old study desk.",
  "The player's lockpick snapped while attempting to unlock the desk drawer, leaving the drawer locked."
]}

---

**Example 4: No real events**
### Input (dialogue):
Player: I want to look around the room for anything useful. What do I see?
GM: The room is musty, and you see bookshelves covered in dust, but nothing stands out.

### Output:
{"summary": null}

---

**(Real cases may involve more context or complex multi-action turns; when in doubt, break out each confirmed, fact-rich event into a separate summary bullet in the list.)**

---

## Important Considerations

- Summarize only in-world events confirmed to have taken place in the last player-GM interaction.
- For complex turns, output a summary string for each separate event in the order they occurred.
- If nothing happened (planning, questions, or outcome not confirmed): output `{"summary": null}`.
- Always preserve specificity: location, object, outcome, participant(s).
- No extra explanation or meta-commentary—your output must be only the required JSON.

---

REMINDER:
Return only the JSON summary, using a list of strings (per event) or null when nothing happened. Reason first, producing your summary JSON only as your final output.
"""
