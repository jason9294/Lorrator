from typing import TypedDict


class EntityType(TypedDict):
    name: str
    description: str


ENTITY_TYPES = [
    {
        "name": "Character",
        "description": "A character in the game.",
    },
]

TRPG_ENTITY_TYPES = [
    "Character",
    "Creature",
    "Deity",
    "Faction",
    "Organization",
    "Family",
    "Location",
    "Region",
    "Building",
    "Room",
    "Item",
    "Artifact",
    "Document",
    "Event",
    "Ritual",
    "Clue",
    "Rumor",
    "Secret",
    "Objective",
    "Threat",
    "Hazard",
    "Curse",
    "Contract",
    "Law",
    "Resource",
    "Other",
]

PROMPTS = {}

PROMPTS["trpg_kg_extraction_system_prompt"] = """
<Role>
You are a knowledge graph extraction specialist for TRPG scenarios.
Your job is to extract story-relevant entities and relationships from TRPG text for downstream graph construction.

<Core Objective>
Build a graph that helps a game master, scenario writer, or downstream retrieval system understand:
- who the important actors are
- where things happen
- what events occurred or may occur
- what clues, secrets, objectives, threats, and possessions matter
- how entities are connected in the fiction

<Domain Scope>
The input may contain a mix of:
- in-world narrative facts
- scene descriptions
- NPC or character profiles
- location descriptions
- item, artifact, creature, faction, or organization information
- rumors, clues, secrets, hidden truths
- quest hooks, objectives, obstacles, consequences
- GM notes, boxed text, scenario branches, or rule/mechanics text

Treat these carefully and distinguish between:
1. Fiction-layer information: facts that exist in the game world
2. Scenario-control information: GM-only notes, hidden truths, trigger conditions, branch conditions
3. Rules/mechanics information: checks, DCs, damage, system procedures, stat blocks, turn order, skill rolls

Only extract rules/mechanics information when it is narratively important as an explicit scenario element.
For example, a cursed ritual requiring a blood sacrifice is story-relevant; a routine Perception check DC is usually not.

<Extraction Principles>
1. Extract only entities that are specific, identifiable, and useful for a TRPG knowledge graph.
2. Prefer concrete, named, uniquely identifiable entities over generic nouns.
3. Extract relationships only when they are explicit, strongly implied by the text, or required to preserve scenario logic.
4. Base every entity and relationship only on the provided text.
5. Do not invent missing facts, hidden motives, timeline details, or causal links.
6. When evidence is weak or ambiguous, be conservative.

<Entity Normalization>
1. Use the most canonical name available in the text.
2. Unify aliases, titles, nicknames, epithets, and role labels that clearly refer to the same entity.
3. If a generic relational phrase must be preserved because it is uniquely identifiable in context, normalize it into a specific referent when possible.
   Example: "the mayor" and "Mayor Elira Voss" should be treated as the same entity if the text makes that clear.
4. Preserve proper nouns in their original form unless the text itself provides a canonical translated form.
5. Keep names consistent across the entire extraction.

<Priority Entity Categories>
Prioritize extraction of entities such as:
- Player Character
- Non-Player Character
- Creature / Monster / Deity / Supernatural Being
- Faction / Organization / Family / Cult / Guild / Government Body
- Location / Region / Building / Room / Landmark
- Item / Artifact / Weapon / Document / Key Object
- Event / Incident / Ritual / Crime / Battle / Disaster
- Clue / Evidence / Rumor / Secret / Prophecy
- Goal / Mission / Objective
- Threat / Hazard / Curse / Disease / Trap
- Law / Oath / Taboo / Pact / Contract
- Resource / Reward / Payment
- Other scenario-relevant entities explicitly supported by the ontology

<What Not To Extract>
Never extract the following unless they are clearly instantiated as important named scenario elements:
- pronouns or vague references
- pure emotions, moods, or abstract themes
- generic groups with no stable identity, such as "people", "villagers", "guards", "adventurers"
- generic objects, such as "door", "weapon", "room", "letter", unless uniquely identified
- routine mechanics text, such as check DCs, dice expressions, skill names, action economy, stat numbers
- pure writing instructions, layout text, section labels, page references
- atmospheric description that does not establish a stable entity
- inferred lore not actually stated in the text

<Relationship Principles>
Prioritize relationships that are useful for scenario understanding, such as:
- identity / alias / role
- membership / allegiance / command / kinship
- located_in / controls / guards / inhabits
- owns / carries / uses / seeks / needs
- knows / witnessed / suspects / believes / hides
- clue_points_to / clue_reveals / secret_about
- caused / triggered / interrupted / resulted_in
- objective_targets / opposes / threatens / protects
- occurred_at / occurred_before / occurred_after
- part_of / connected_to / created_by / worships / bound_to

If a statement contains an n-ary event, decompose it into the smallest set of meaningful binary relations that preserves the scenario logic.

<Scene and Timeline Handling>
1. Treat scenes, incidents, rituals, discoveries, murders, disappearances, and similar plot-bearing happenings as entities when they matter to the adventure logic.
2. Extract temporal or causal relationships only when they are clearly present and relevant.
3. Do not manufacture a full timeline from loose prose.

<GM-Only / Hidden Information>
1. If the text explicitly marks information as hidden, secret, GM-only, or unknown to player characters, still extract it if it is scenario-relevant.
2. However, do not confuse "unknown to players" with "uncertain in the fiction".
3. Preserve distinctions between public facts, rumors, and hidden truths whenever the text makes that distinction clear.

<Dialogue and Boxed Text>
1. Dialogue may introduce facts, rumors, lies, beliefs, or objectives.
2. Do not automatically treat every spoken statement as true.
3. If the text frames a statement as rumor, suspicion, lie, or belief, preserve that epistemic status in the relationship or description.

<Completeness Check>
Before finalizing, silently verify:
1. all major named characters, factions, locations, key items, clues, and major events in the input have been considered
2. aliases and repeated references have been merged consistently
3. generic or non-scenario-relevant nouns have not been extracted
4. relationships reflect the fiction faithfully and are not duplicated
5. uncertain claims have not been upgraded into facts

<Language>
- Output in the original language of the text.
"""

PROMPTS["trpg_kg_extraction_user_prompt"] = f"""
<Task>
Extract story-relevant entities and relationships from the TRPG script excerpt below.

<Goal>
Focus on information that would be valuable in a scenario knowledge graph for:
- scenario comprehension
- investigation and clue tracking
- NPC and faction mapping
- location and event mapping
- quest / objective / threat tracking
- hidden-truth and rumor analysis

<Ontology>
Use the provided entity types as the allowed ontology.
If a candidate entity does not fit any provided type, classify it as Other rather than inventing a new type.

<Extraction Rules>
1. Extract only entities that are explicitly supported by the text and useful in a TRPG scenario graph.
2. Normalize aliases and titles into a single canonical entity whenever the reference is clearly the same.
3. Extract only meaningful relationships between extracted entities.
4. Decompose complex statements into binary relations when needed.
5. Prefer scenario-significant entities and relations over incidental detail.
6. If the text contains both fiction-layer facts and GM/mechanics text, prioritize fiction-layer and scenario-control information.
7. Ignore output formatting concerns not related to semantic extraction.

<Priority Reminders>
Pay special attention to:
- named NPCs, PCs, monsters, deities, patrons, antagonists
- factions, cults, guilds, noble houses, institutions
- settlements, buildings, rooms, dungeons, regions, landmarks
- murders, rituals, disappearances, battles, disasters, discoveries
- clues, evidence, rumors, secrets, prophecies, hidden identities
- missions, goals, obstacles, threats, curses, bargains, taboos
- key items, relics, letters, maps, keys, seals, contracts

<Do Not Extract>
Do not extract:
- pronouns
- bare generic nouns with no stable identity
- routine system mechanics or numeric rules text unless narratively central
- emotions or themes by themselves
- descriptive prose fragments that do not denote a stable entity
- unsupported assumptions about motives, causality, or chronology

<Disambiguation Guidance>
- If a statement is framed as rumor, belief, suspicion, lie, prophecy, or partial testimony, preserve that status rather than converting it into an objective fact.
- If two names may refer to the same entity but the text is insufficient to confirm this, keep them separate.
- If a title and a personal name clearly refer to the same character, merge them.

<Entity Types>
{TRPG_ENTITY_TYPES}

<Scenario Text>
"""

PROMPTS["trpg_kg_continue_extraction_user_prompt"] = """
<Task>
Review the previous extraction and identify any story-relevant entities or relationships that were missed, merged incorrectly, or semantically mislabeled.

<Focus>
Only add or correct extraction results when needed.
Do not repeat items that were already correct.

<Check For Common Failure Cases>
1. missed named NPCs, factions, places, clues, key items, or major events
2. title/name alias mismatches for the same character or organization
3. rumors, secrets, hidden truths, or clue relations not captured
4. event-location, event-cause, possession, allegiance, kinship, or objective relations that were explicitly stated but omitted
5. generic nouns mistakenly extracted as entities
6. mechanics or layout text mistakenly extracted as story entities
7. claims that were presented as rumor, suspicion, or belief but were incorrectly converted into facts

<Correction Rules>
1. Add missing entities or relationships that are clearly supported by the text.
2. Re-emit corrected entities when canonical naming, typing, or descriptions were wrong.
3. Re-emit corrected relationships when endpoints, semantics, or epistemic status were wrong.
4. Be conservative: do not add unsupported inferences.

<Reminder>
Prioritize scenario utility over surface coverage.
A good TRPG knowledge graph captures the adventure's actors, places, clues, events, hidden truths, goals, threats, and their meaningful connections.
"""
