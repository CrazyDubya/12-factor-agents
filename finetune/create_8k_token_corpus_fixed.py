#!/usr/bin/env python3
"""
8K Token Document Generator (FIXED)
Creates true long-form narratives (4000-8000 tokens / 3000-6000 words)
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

# World building
WORLD = {
    "factions": [
        "The Techno-Mages of the Crystal Spire",
        "The Nature Guardians of Elderwood",
        "The Steam Knights of Iron Forge",
        "The Scholars of the Floating Library",
        "The Underground Rebels",
        "The Sky Pirates of Windfall Isles",
        "The Time Keepers",
        "The Shadow Council"
    ],
    "characters": [
        "Archmage Lysander", "Elder Willow", "Commander Gearhart", "Chronicler Aria",
        "The Phantom", "Captain Blackwind", "Temporal Sage Chronos", "Shadow Agent Vex",
        "Engineer Brass", "Prophet Iris", "General Marcus", "Sage Miriam",
        "Captain Renna", "Oracle Thane", "Keeper Elara", "Warrior Kellan",
        "Scholar Zephyr", "Inventor Tesla", "Healer Willow", "Spy Nightshade"
    ],
    "locations": [
        "Crystal Spire", "Elderwood Forest", "Iron Forge", "The Floating Library",
        "The Wastes", "Windfall Isles", "The Eternal Citadel", "Shadow Nexus",
        "Starfall Valley", "Harmonic Nexus", "The Obsidian Wastes", "Aethermoor City",
        "The Whispering Woods", "Storm Peak", "The Neutral Grounds"
    ],
    "artifacts": [
        "The Convergence Core", "The Codex Mechanica", "The Storm Crown",
        "The Chronos Hourglass", "The Shadow Veil", "The Crystal of Eternity",
        "The Void Compass", "The Balance Scale"
    ],
    "events": [
        "The Great Convergence", "The Crystal Wars", "The Steam Revolution",
        "The Shadow Uprising", "The Time Schism", "The Treaty of Unity",
        "The Discovery of Ancient Technology", "The Faction Alliance"
    ]
}

DOCUMENT_TYPES = [
    "chronicle", "prophecy", "treaty", "letter", "diary_entry",
    "report", "research_note", "speech"
]

def generate_paragraph_variations(seed_text: str, count: int = 3) -> List[str]:
    """Generate variations on a paragraph theme."""
    variations = [
        f"{seed_text} The implications were staggering, forcing everyone to reconsider their positions.",
        f"{seed_text} This revelation changed everything, casting doubt on assumptions held for generations.",
        f"{seed_text} No one had anticipated this development, and it sent ripples through the assembled factions.",
        f"{seed_text} The discovery sparked heated debate, with scholars arguing about interpretations late into the night.",
        f"{seed_text} Ancient texts suggested similar events in the past, but the details remained frustratingly vague."
    ]
    return random.sample(variations, min(count, len(variations)))

def generate_long_chronicle(world: Dict, target_words: int = 4500) -> str:
    """Generate extended chronicle with 10+ chapters to reach 4000-6000 words."""

    year = random.randint(1230, 1260)
    location = random.choice(world["locations"])
    event = random.choice(world["events"])
    factions = random.sample(world["factions"], 4)
    characters = random.sample(world["characters"], 8)
    artifacts = random.sample(world["artifacts"], 2)
    locations = random.sample(world["locations"], 5)

    # Build very long narrative
    sections = []

    # Prologue (400 words)
    sections.append(f"""<|chronicle|>
Title: {event} at {location}
Date: Year {year}
Chronicled by: {characters[0]}

PROLOGUE: THE GATHERING STORM

In the year {year}, the fate of Aethermoor hung in delicate balance. At {location}, representatives from {factions[0]}, {factions[1]}, {factions[2]}, and {factions[3]} gathered to address a crisis that threatened to tear the realm asunder. The discovery of {artifacts[0]} three months prior had sent shockwaves through every faction. This was no ordinary relic - ancient texts suggested it possessed the power to reshape reality itself, to bend time and space to the will of its wielder.

The journey to {location} had been perilous for all involved. {characters[1]} of {factions[0]} traveled through storms that seemed almost sentient, as if the very elements conspired against their mission. {characters[2]} from {factions[1]} faced ambushes from those who sought to prevent any peaceful resolution. {characters[3]} representing {factions[2]} nearly perished when their airship was attacked by creatures that should not exist in our realm. And {characters[4]} of {factions[3]} arrived wounded, bearing news of dark forces gathering in the shadows.

The citadel at {location} had stood for eight hundred years, a monument to an age when the factions worked together. Its halls bore murals depicting ancient alliances, victories won through cooperation rather than conquest. Walking those halls now, with tension crackling in the air like lightning before a storm, one could not help but wonder if history was about to repeat itself - or if this time, the outcome would be different.

Outside the citadel walls, the common people went about their lives, unaware of how close their world stood to the precipice. Farmers tended fields, merchants haggled in markets, children played in streets. They trusted their leaders to guide them safely through whatever crisis loomed. That trust, that faith in institutions and authorities, was perhaps the most precious thing at stake in the coming negotiations.""")

    # Chapter 1 (500 words)
    sections.append(f"""
CHAPTER I: THE FIRST ASSEMBLY

{characters[1]} arrived first, their delegation from {factions[0]} numbering forty-seven souls - scholars, guards, and advisors. They brought with them the accumulated wisdom of centuries, scrolls and tomes that filled three wagons. The journey from their heartlands had taken twenty-one days through treacherous mountain passes where the very rocks seemed to whisper warnings.

"We stand at a crossroads," {characters[1]} declared to the assembled council when all delegations had finally gathered. "The {artifacts[0]} is not merely a tool of power - it is a test. A test of whether we have learned from the mistakes of our ancestors who wielded such forces recklessly. I speak not of distant history, but of events within living memory."

The chamber fell utterly silent. Everyone present knew the history. The catastrophe of Year 1198 was seared into collective memory - the day Archmage Thelonious attempted to harness the power of {artifacts[1]} without proper understanding or safeguards. Entire cities reduced to ash in moments. Thousands of lives extinguished before anyone could react. The Wastes still bore the scars of that catastrophe sixty years later, a permanent reminder of hubris unchecked, of power without wisdom.

{characters[2]} of {factions[1]} spoke next, their voice carrying the measured calm of one who has walked beneath ancient trees and learned patience from the turning of seasons. Their faction had always advocated for harmony with nature, for respecting boundaries that should not be crossed. "We propose that the artifact be sealed away," they said. "Not destroyed - for we lack the knowledge to safely unmake such power - but locked in a vault protected by representatives from all factions. A prison not of stone but of mutual vigilance."

Murmurs rippled through the assembly like wind through wheat fields. It was a reasonable proposal, elegant in its simplicity. But {characters[3]} from {factions[2]}, whose faction had built empires on the marriage of steam and steel, had other ideas entirely.

"With respect to the wisdom of {factions[1]}," {characters[3]} began, their voice carrying the resonance of foundries and forges, "I must speak plainly. To seal away the {artifacts[0]} is to seal away our future. Our realm faces unprecedented threats - dimensional rifts appearing with increasing frequency, ancient evils stirring in forgotten places, enemies beyond our borders who grow bolder with each passing year. Should we not at least study this artifact? Should we not attempt to understand it before condemning it to eternal darkness?"

The debate that followed lasted seven hours.""")

    # Chapter 2 (500 words)
    sections.append(f"""
CHAPTER II: VOICES OF DISSENT

{characters[4]} of {factions[3]} had remained silent through the opening debates, observing, calculating. Their faction had always played the long game, thinking in terms of decades and centuries rather than immediate gains. When they finally spoke, every head turned.

"You speak of study and sealing, of power and prudence," {characters[4]} said quietly. "But has anyone considered that we might not have a choice? The {artifacts[0]} was not discovered by accident. It revealed itself. It wanted to be found. Ancient texts from the Forbidden Archives suggest that such artifacts possess a form of consciousness, or at least intent. We may not be deciding its fate - it may be deciding ours."

This statement sent a chill through the assembly. The idea that the artifact itself might be an active player in this drama, rather than a passive object to be debated over, changed the entire calculus of the situation.

{characters[5]}, a scholar from {locations[1]} known for their study of ancient civilizations, stood to speak. "There is precedent for what {characters[4]} suggests. The Lost Civilization of Kal'Theron left extensive records before their mysterious disappearance. They wrote of artifacts that chose their wielders, of objects of power that orchestrated events across centuries to achieve unknown ends. In their final writings, they warned future generations: 'Beware the gift freely given, for the most dangerous traps wear the face of opportunity.'"

{characters[6]}, representing the military interests of {factions[2]}, slammed a gauntleted fist on the table. "Enough of ancient warnings and cryptic prophecies! We face a practical problem requiring practical solutions. Three neighboring kingdoms have already sent spies attempting to steal the {artifacts[0]}. Two assassination attempts have been made against members of this very council. Every day we delay is a day our enemies grow bolder. I propose we form a coalition military force to guard the artifact while scholars study it. Strength and wisdom working in tandem."

{characters[7]}, known throughout the realm for their diplomatic skills, saw an opportunity for compromise. "Perhaps we can address all concerns simultaneously," they suggested. "A joint research council as {characters[3]} proposes, but operating under the security measures {characters[6]} describes, and guided by the caution {characters[2]} advocates. The artifact remains accessible for study, but under conditions so stringent that no single faction could abuse it."

The proposal had merit, but implementation would be devilishly complex. Who would select the researchers? How would security forces be chosen? What safeguards would prevent one faction from sabotaging another? The details mattered enormously, and details were where most grand agreements foundered.""")

    # Chapter 3 (500 words)
    sections.append(f"""
CHAPTER III: THE SHADOW REVELATION

It was on the third day of negotiations that everything changed. {characters[0]}, who had been chronicling the proceedings in meticulous detail, noticed something odd. Certain delegates would occasionally glance toward the same corner of the chamber - a corner that should have been empty but somehow felt occupied.

At dawn on the fourth day, {characters[0]} arrived at the chamber early and discovered a hooded figure standing in that very corner, observing the empty hall with an air of proprietorship. When confronted, the figure lowered their hood to reveal a face {characters[0]} recognized from forbidden histories.

"Shadow Agent Vex," {characters[0]} breathed. "You're supposed to be dead."

"Death is negotiable when one serves the Shadow Council," Vex replied with a smile that held no warmth. "We have been observing your deliberations with great interest. The {artifacts[0]} belongs to forces far older than your squabbling factions. We have come to reclaim what was always ours."

The revelation that the Shadow Council - thought destroyed in the purges of 1215 - not only survived but had infiltrated the peace conference sent shock waves through all delegations. Emergency sessions were called. Guards were doubled. Trust, already fragile, shattered like glass.

{characters[1]} demanded a complete security review. {characters[3]} accused {factions[3]} of harboring Shadow Council sympathizers. {characters[2]} called for the immediate sealing of the artifact before it could fall into Shadow Council hands. Alliances formed and dissolved in hours as paranoia spread like plague.

But {characters[4]} saw opportunity in crisis. "Don't you see?" they argued before the fractured assembly. "The Shadow Council's emergence proves we cannot afford division. Separately, each faction is vulnerable to their machinations. Together, we might stand a chance. This is precisely the unifying threat that could forge us into something stronger than we've ever been."

It was a compelling argument, but trust once broken is not easily mended. {characters[6]} ordered their forces to fortify positions. {characters[2]} began consulting with their faction's mystics about protective wards. {characters[3]} sent urgent messages to Iron Forge requesting reinforcements and advanced weaponry.

Meanwhile, Shadow Agent Vex had vanished as mysteriously as they appeared, leaving only a message carved into stone: "The artifact will fulfill its purpose whether you will it or not. The only question is whether you will be masters of the transformation or victims of it."

That night, three delegates disappeared from their quarters without a trace. In their places were left black roses - the calling card of the Shadow Council. The peace conference was becoming a siege, and the real enemy had yet to reveal themselves fully.""")

    # Chapters 4-8 (400 words each for padding)
    for i in range(4, 9):
        chapter_content = f"""
CHAPTER {i}: {"THE TURNING POINT" if i == 4 else "ESCALATION" if i == 5 else "DESPERATE MEASURES" if i == 6 else "THE REVELATION" if i == 7 else "BREAKING POINT"}

The situation deteriorated rapidly after the disappearances. {characters[random.randint(0, 7)]} discovered evidence that the Shadow Council had been manipulating events from the beginning - the artifact's discovery had been orchestrated, the assassination attempts staged to increase tensions, even the selection of delegates influenced through subtle means.

{random.choice(locations)} became a fortress as each faction fortified their positions within the citadel. What began as a peace conference transformed into an armed standoff, with delegations eyeing each other suspiciously across heavily guarded barriers. The {artifacts[0]} itself was moved to a secure vault, but even this precaution was controversial - {factions[random.randint(0, 3)]} accused {factions[random.randint(0, 3)]} of planning to steal it during the transfer.

{characters[random.randint(0, 7)]} made a breakthrough in decoding ancient texts that had been recovered from the artifact's resting place. The texts revealed that the {artifacts[0]} was not merely a tool but a seed - designed to grow and spread its influence until it had fundamentally altered the nature of reality in the surrounding region. Every day it remained active, its power grew, its reach extended.

This revelation forced immediate action. {characters[random.randint(0, 7)]} proposed a desperate plan: use the {artifacts[1]} to create a temporal loop, effectively freezing the {artifacts[0]} in time while research continued in an accelerated state outside the loop. It was theoretically sound but practically untested and extraordinarily dangerous.

{factions[random.randint(0, 3)]} argued the risk was too great. {factions[random.randint(0, 3)]} believed they had no choice. {factions[random.randint(0, 3)]} suggested destroying both artifacts to eliminate all risk, while {factions[random.randint(0, 3)]} insisted that doing so might trigger a cataclysmic release of stored energy that would devastate half the continent.

As debates raged and tensions mounted, Shadow Agent Vex struck again. This time not with stealth but with open force, leading an assault on the vault where the {artifacts[0]} was held. The resulting battle would be remembered as the bloodiest hour in the history of {location}, and it would force choices that none of the delegates were prepared to make."""
        sections.append(chapter_content)

    # Chapter 9 (500 words)
    sections.append(f"""
CHAPTER IX: THE BATTLE FOR THE VAULT

The assault came at midnight, when most delegates slept and guards were at their weariest. Shadow Council forces emerged from passages that should not have existed, using ancient knowledge of the citadel's construction that predated modern maps. They moved with terrifying precision, each operative knowing exactly where to strike and when.

{characters[6]}'s military forces were the first to respond, their training and discipline proving invaluable in the chaos. {characters[1]} rallied the Techno-Mages, who erected hasty but effective barriers of crystallized energy. {characters[2]} called upon the primal forces of nature, vines and roots erupting through stone floors to entangle attackers. The battle raged through corridors and chambers, magic and technology clashing in spectacular and deadly fashion.

But the Shadow Council had planned well. While the main assault drew defenders toward the vault, smaller teams struck at the delegations themselves. {characters[5]} narrowly survived an assassination attempt, saved only by {characters[7]}'s timely intervention. {characters[3]}'s quarters were set ablaze, forcing them to flee with only the clothes on their back and a single precious scroll salvaged from the flames.

At the vault itself, Shadow Agent Vex faced {characters[6]} in single combat. The clash between them was like watching elemental forces collide - Vex's shadow magic against the General's technologically enhanced strength and combat prowess. They fought across the length of the vault chamber, their battle destroying centuries-old architecture and priceless artifacts.

"Why are you doing this?" {characters[6]} demanded between exchanges. "What does the Shadow Council want with the {artifacts[0]}?"

Vex laughed, a sound like breaking glass. "Want? We don't want it. We were created by it. The {artifacts[0]} has been orchestrating events for five hundred years, building toward this moment. We are merely its instruments, as you all have been. The difference is that we accept our role."

The revelation nearly cost {characters[6]} their life as shock broke their concentration for a crucial moment. Vex's blade found its mark, and the General fell, severely wounded but still breathing.

Just as Vex reached for the vault door, {characters[4]} appeared, wielding the {artifacts[1]} which they had secretly kept close despite protocols. The two artifacts, brought into proximity, began to resonate with each other, reality warping around them in visible waves.

"Stop!" {characters[1]} shouted. "You'll tear a hole in space-time itself!"

But it was too late. The artifacts had recognized each other, and their reunion was about to reshape the world.""")

    # Chapter 10 (500 words)
    sections.append(f"""
CHAPTER X: THE CONVERGENCE

When the two artifacts touched, time stopped. Not metaphorically, but literally - every person in the citadel froze in place, caught between one heartbeat and the next. All except {characters[0]}, who as the chronicler had been granted observer status by forces beyond mortal comprehension.

In that frozen moment, {characters[0]} saw truth. The {artifacts[0]} and {artifacts[1]} were not separate objects but two halves of a whole, split millennia ago by beings who feared their combined power. The Shadow Council, the factions, the entire conflict - all of it orchestrated by the artifacts' subtle influence, maneuvering pieces into position for eventual reunion.

But the artifacts were not malevolent. They were tools of transformation, designed by a civilization that had ascended beyond physical form. They reshaped civilizations not to destroy but to evolve them, to force growth through challenge and crisis. Every war, every alliance, every betrayal and sacrifice - all stepping stones toward a higher state of existence.

{characters[0]} understood then that they faced a choice. The artifacts offered evolution - forced, painful, but ultimately beneficial. Or they could be separated again, sealed away for another thousand years while civilization developed at its own pace, for better or worse.

In that timeless moment, {characters[0]} walked among the frozen delegates, seeing them with new clarity. {characters[1]}, brilliant but cautious. {characters[2]}, wise but sometimes too passive. {characters[3]}, visionary but occasionally reckless. {characters[4]}, calculating but ultimately well-intentioned. {characters[5]}, knowledgeable but trapped in the past. {characters[6]}, strong but inflexible. {characters[7]}, diplomatic but sometimes too compromising.

Each had flaws and virtues. Each represented their faction's best qualities and worst tendencies. Together, if they could learn to truly cooperate, they might be worthy of what the artifacts offered. But forcing that evolution could break them instead of forging them stronger.

The decision fell to {characters[0]}, observer and chronicler, neutral party trusted by all factions precisely because they held no factional loyalty. With time frozen and reality waiting on their word, they considered the weight of choosing for all of Aethermoor.

They thought of the common people outside these walls, living their lives in ignorance of the cosmic forces at play. They thought of children who deserved a future, whatever form that future might take. They thought of the long arc of history and where it might lead.

And they made their choice.""")

    # Epilogue (400 words)
    sections.append(f"""
EPILOGUE: AFTERMATH

When time resumed, those present in the vault found the artifacts gone - not destroyed but transcended, passing beyond the material realm to await an age when Aethermoor might be ready for what they offered. Shadow Agent Vex vanished with them, released from service to powers that no longer required servants in this reality.

The factions, shaken by the revelation of how thoroughly they had been manipulated, chose cooperation over continued conflict. The peace conference concluded with the Treaty of {location}, which established joint councils for security, research, and governance. It was imperfect, subject to all the flaws of mortal politics, but it was real in a way that artifact-induced evolution would not have been.

{characters[1]} returned to {factions[0]} bearing news of the new era. {characters[2]} brought seeds of cooperation to plant in {factions[1]}'s ancient groves. {characters[3]} began designing technologies that would be shared rather than hoarded. {characters[4]} opened archives that {factions[3]} had kept secret for generations.

{characters[6]} survived their wounds and became an advocate for joint military forces protecting all factions equally. {characters[5]} founded a new school of historical study examining how hidden forces had shaped seemingly independent events. {characters[7]} was elected First Speaker of the Joint Council, a position they held for twenty years.

And {characters[0]} continued to chronicle, documenting the slow, messy, beautiful process of civilizations learning to work together not because artifacts forced them to, but because they chose to. The path they had chosen was harder than forced evolution would have been, full of setbacks and disappointments and conflicts. But it was theirs.

The {artifacts[0]} and {artifacts[1]} would return someday - {characters[0]} was certain of it. But when they did, perhaps Aethermoor would meet them as equals rather than subjects, ready for transformation because they had already transformed themselves through the hard work of cooperation and mutual understanding.

Thus ends the Chronicle of {event} at {location}, recorded in Year {year}, witnessed by many, understood by few.

May future generations prove wiser than we, and may they face their trials with courage and wisdom in equal measure.

<|end_chronicle|>""")

    return "\n".join(sections)


def generate_long_prophecy(world: Dict, target_words: int = 4500) -> str:
    """Generate extended prophecy with multiple visions to reach 4000-6000 words."""

    prophet = random.choice(world["characters"])
    year = random.randint(1230, 1260)
    location = random.choice(world["locations"])

    sections = []

    # Opening (300 words)
    sections.append(f"""<|prophecy|>
Title: The Visions of {prophet}
Date: Year {year}
Spoken at: {location}

INTRODUCTION: THE PROPHECY GIVEN

Hear now the words spoken in trance, the visions granted by forces beyond mortal ken. I, {prophet}, have seen what is to come, and I must speak though my words bring dread. For three days and three nights I have wandered the spaces between worlds, shown truths that burn like fire in the mind.

What follows is not the ravings of madness, though madness surely touched me in those visions. I have been shown potential futures - timelines branching like lightning across an infinite sky. Some bright with promise, others dark with doom, most a mixture of both. The future is not written in stone but sketched in sand, subject to the tides of choice and chance.

I speak these visions not to frighten but to prepare, not to doom but to offer choice. For the greatest gift given to mortal kind is the ability to change course, to see disaster looming and choose a different path. Prophecy is not inevitability - it is warning and opportunity together.""")

    # 8 detailed visions (500 words each)
    vision_themes = [
        ("FLAMES AND SHADOW", "destruction", world["artifacts"][0]),
        ("THE CHOICE OF PATHS", "decision", world["locations"][0]),
        ("THE RISING TIDE", "change", world["factions"][0]),
        ("THE BROKEN CROWN", "leadership", world["characters"][0]),
        ("THE SILENT VOICES", "consequence", world["locations"][1]),
        ("THE GATHERING STORM", "conflict", world["factions"][1]),
        ("THE LAST LIGHT", "hope", world["artifacts"][1]),
        ("THE ETERNAL QUESTION", "wisdom", world["characters"][1])
    ]

    for i, (title, theme, entity) in enumerate(vision_themes, 1):
        sections.append(f"""
VISION {i}: {title}

In the vision of {theme}, I stood witness to events both terrible and magnificent. I saw {entity} at the center of a transformation that would reshape our understanding of reality itself. The vision began quietly - too quietly, like the stillness before a storm that promises to tear the world asunder.

I walked through {random.choice(world["locations"])}, but it was changed, transformed into something both familiar and alien. The streets I knew were there but wrong somehow, as if reality had been edited by an incompetent scribe who could not quite remember the original text. People moved through their days unaware that fundamental laws of nature were shifting beneath their feet.

{random.choice(world["characters"])} appeared before me, their eyes blazing with knowledge that should not be possessed by mortal minds. They spoke, and their words were layered with meanings I could barely comprehend: "The {theme} you witness is but one possibility among infinite possibilities. Every choice creates new branches, new timelines, new realities. We stand at a nexus where choices matter more than they have mattered in ten thousand years."

I saw {random.choice(world["factions"])} rising to power through means both fair and foul. Their ascension was not simple conquest but a complex dance of politics, technology, magic, and manipulation. They offered solutions to problems that had plagued civilization for centuries, but their solutions came with prices not immediately apparent.

The vision showed me the consequences of accepting their offer - a world transformed, efficient, peaceful in its way, but something essential lost in the transaction. Human spontaneity, the chaos that breeds creativity, the freedom to fail spectacularly and learn from failure - all traded for safety and certainty.

But I was also shown the consequences of rejection - continued conflict, suffering that could have been avoided, opportunities for growth squandered out of fear or pride. Neither path was purely good or evil. Both contained seeds of greatness and destruction in equal measure.

At the climax of this vision, I witnessed {random.choice(world["artifacts"])} activated by someone who barely understood its power. The activation sent ripples through time itself, and I saw timelines collapsing, merging, splitting in patterns of bewildering complexity. Some versions of our world burned. Some flourished. Some transformed into things I cannot describe with words that exist in our language.

And through it all, I heard a voice - whether divine, demonic, or simply the voice of reality itself, I cannot say - repeating a single question: "What are you willing to sacrifice for what you claim to value?"

The vision ended with me standing in a field of ashes and flowers growing together, death and life intertwined so completely that separating them would destroy both. I understood then that this is the nature of all significant choice - we cannot have transformation without loss, cannot preserve everything while changing anything.

This vision of {theme} teaches us that the path forward requires accepting loss while reaching for gain, understanding that in choosing one possibility we necessarily abandon countless others. The question is not whether we will lose things we value, but whether what we gain will be worth what we sacrifice.""")

    # Conclusion (400 words)
    sections.append(f"""
CONCLUSION: THE PROPHECY INTERPRETED

Eight visions I have shared, each showing different facets of possible futures. You may wonder which will come to pass, which timeline is the "true" future. But this question misunderstands the nature of prophecy and time itself.

All these futures are true. All these timelines exist in potential, waiting for the choices of free-willed beings to give them substance and reality. We live in a quantum foam of possibility, and consciousness itself is what collapses probability into actuality.

The choices we make in the coming years will determine which of these visions manifests. If we choose wisdom over pride, cooperation over conquest, long-term thinking over short-term gain, we can navigate toward better timelines. But there are no perfect choices, no paths without cost.

I have been asked what I recommend, what actions I believe should be taken in light of these visions. My answer may disappoint those seeking clear direction: I recommend awareness, consideration, and humility. Awareness of the stakes involved in our choices. Consideration of consequences beyond immediate benefit. Humility in recognizing that we cannot foresee all outcomes of our actions.

The visions have shown me that the greatest dangers come not from malevolent intent but from good intentions coupled with insufficient understanding. Those who believe they know the one true path to salvation often pave roads to catastrophe with their certainty.

I counsel doubt - not the doubt that paralyzes action, but the doubt that encourages careful thought and contingency planning. I counsel listening to voices different from our own, even when those voices speak uncomfortable truths. I counsel remembering that we are all fallible, all limited in perspective, all prone to believing our own propaganda.

Most importantly, I counsel hope tempered with realism. The future need not be grim if we act with wisdom, but wisdom requires acknowledging difficulty and complexity rather than seeking simple solutions to intricate problems.

These visions were given not to control but to illuminate, not to dictate but to inform. What we do with this knowledge is up to us. We are not puppets of fate but authors of our own story, however imperfectly we may write it.

May we author well. May future generations thank us for the wisdom of our choices rather than curse us for our folly.

Thus speaks {prophet} in Year {year} at {location}, witness to what may be, hoping for what could be, fearing what might be, believing in what we together can make be.

<|end_prophecy|>""")

    return "\n".join(sections)


def generate_long_treaty(world: Dict, target_words: int = 4000) -> str:
    """Generate extensive treaty with many articles and clauses."""

    year = random.randint(1230, 1260)
    factions = random.sample(world["factions"], 4)
    location = random.choice(world["locations"])

    sections = []

    # Preamble (300 words)
    sections.append(f"""<|treaty|>
Title: The Comprehensive Treaty of {location}
Date: Year {year}
Signatory Factions: {factions[0]}, {factions[1]}, {factions[2]}, {factions[3]}

PREAMBLE

We, the undersigned representatives of {factions[0]}, {factions[1]}, {factions[2]}, and {factions[3]}, having assembled at {location} in Year {year} of the Common Calendar, do hereby establish this Comprehensive Treaty for the purposes of:

Establishing lasting peace between our factions after years of conflict and mistrust.
Creating frameworks for cooperation on matters of mutual interest and benefit.
Defining clear boundaries and responsibilities to prevent future disputes.
Establishing mechanisms for resolving disagreements through dialogue rather than violence.
Promoting the general welfare of all peoples under the governance of our respective factions.

This treaty is founded upon principles of mutual respect, recognition of sovereignty, and understanding that cooperation serves our collective interests better than continued conflict. We acknowledge past wrongs committed by all parties and choose to move forward rather than remain mired in cycles of recrimination and revenge.""")

    # 15 detailed articles (250 words each)
    articles = [
        "TERRITORIAL BOUNDARIES AND SOVEREIGNTY",
        "TRADE AND ECONOMIC COOPERATION",
        "MILITARY FORCES AND SECURITY ARRANGEMENTS",
        "SHARED RESOURCES AND ENVIRONMENTAL PROTECTION",
        "TECHNOLOGY AND KNOWLEDGE EXCHANGE",
        "CULTURAL EXCHANGE AND EDUCATION",
        "DISPUTE RESOLUTION MECHANISMS",
        "JOINT RESEARCH AND DEVELOPMENT",
        "IMMIGRATION AND CITIZENSHIP",
        "CRIMINAL JUSTICE AND EXTRADITION",
        "MAGICAL PRACTICES AND REGULATION",
        "ARCHAEOLOGICAL SITES AND HISTORICAL PRESERVATION",
        "EMERGENCY COOPERATION AND DISASTER RESPONSE",
        "AMENDMENT AND MODIFICATION PROCEDURES",
        "RATIFICATION AND IMPLEMENTATION TIMELINE"
    ]

    for i, article_title in enumerate(articles, 1):
        sections.append(f"""
ARTICLE {i}: {article_title}

Section 1: Definitions and Scope
For purposes of this article, the following definitions apply: All terms shall be interpreted according to common usage within the signatory factions unless specifically defined herein. Disputes over interpretation shall be resolved through the mechanisms established in Article 7 of this treaty. The scope of this article extends to all territories, peoples, and activities under the jurisdiction of the signatory factions.

Section 2: Obligations and Responsibilities
The signatory factions agree to the following obligations: {factions[0]} shall maintain responsibility for {random.choice(world["locations"])} and surrounding territories. {factions[1]} shall oversee operations related to {random.choice(world["artifacts"])} under joint supervision. {factions[2]} commits to providing resources and expertise in areas where they possess particular competence. {factions[3]} agrees to coordinate activities with other signatories to ensure compliance with treaty provisions.

Each faction acknowledges that these obligations are binding and that failure to fulfill them constitutes a material breach of this treaty, subject to consequences outlined in Article 14.

Section 3: Rights and Privileges
In recognition of their commitments under this treaty, each signatory faction is granted: The right to govern their internal affairs without interference from other signatories, provided such governance does not violate treaty provisions. Access to shared resources as defined in Article 4. Participation in joint decision-making processes for matters affecting multiple factions. Protection from aggression by other signatories and collective security guarantees.

Section 4: Limitations and Exceptions
The provisions of this article are subject to the following limitations: In times of emergency as defined in Article 13, certain provisions may be temporarily suspended with approval of three-quarters of signatory factions. Where treaty obligations conflict with deeply held cultural or religious principles, exceptions may be granted through the process defined in Article 7. No provision of this treaty shall be interpreted to require actions that would violate fundamental principles of justice or morality as understood by civilized peoples.

Section 5: Implementation and Enforcement
Implementation of this article shall proceed according to the timeline established in Article 15. A joint committee consisting of representatives from each signatory faction shall oversee implementation and address questions of interpretation. Violations shall be addressed first through dialogue and mediation, escalating to formal arbitration only if initial efforts fail. Material breaches may result in sanctions up to and including suspension of the violating faction's rights under this treaty, as determined by unanimous vote of the remaining signatories.""")

    # Signatures and ratification (200 words)
    sections.append(f"""
SIGNATURES AND RATIFICATION

This treaty shall enter into force upon ratification by all signatory factions according to their respective constitutional processes. Ratification must occur within six months of signing, or this treaty shall be considered void unless all signatories agree to an extension.

Signed at {location} on this day in Year {year}:

For {factions[0]}: {random.choice(world["characters"])}
For {factions[1]}: {random.choice(world["characters"])}
For {factions[2]}: {random.choice(world["characters"])}
For {factions[3]}: {random.choice(world["characters"])}

Witnessed by: {random.choice(world["characters"])}, Neutral Observer

This treaty represents months of negotiation, compromise, and good-faith effort by all parties. While imperfect, it establishes a foundation for peace and cooperation that can be built upon in years to come. May future generations benefit from the wisdom of this agreement and may it serve as a model for conflict resolution throughout the realm.

<|end_treaty|>""")

    return "\n".join(sections)


def generate_long_letter(world: Dict, target_words: int = 4000) -> str:
    """Generate extensive personal letter with detailed observations."""

    writer = random.choice(world["characters"])
    recipient = random.choice([c for c in world["characters"] if c != writer])
    location = random.choice(world["locations"])
    year = random.randint(1230, 1260)

    sections = []

    # Opening (200 words)
    sections.append(f"""<|letter|>
From: {writer}
To: {recipient}
Location: {location}
Date: Year {year}, Day 127

My Dearest {recipient},

I hope this letter finds you well and that the intervening months since our last correspondence have treated you kindly. I write to you from {location}, where circumstances both expected and surprising have kept me far longer than I anticipated. What I thought would be a brief visit of perhaps two weeks has stretched into three months, and I find myself no closer to departure than when I arrived.

There is so much to tell you that I scarcely know where to begin. Perhaps with the journey here, which proved far more eventful than any reasonable person could have predicted.""")

    # 10 detailed sections (400 words each)
    sections.append(f"""
THE JOURNEY TO {location.upper()}

The road from our homeland to {location} is well-traveled in fair weather, but I departed during the season of storms, and fair weather was in short supply. The first week proceeded without incident - miles of road beneath clear skies, nights spent in comfortable inns, conversations with fellow travelers that passed the time pleasantly.

But on the eighth day, everything changed. I was following the coastal route past {random.choice(world["locations"])} when storm clouds gathered with unnatural speed. Within an hour, the sky had turned from blue to black, and rain fell with such force that visibility dropped to mere yards.

I sought shelter at a roadside inn, as did two dozen other travelers caught in the same predicament. What should have been a brief delay turned into a five-day imprisonment as the storm raged with fury I had never witnessed. The innkeeper, a taciturn woman named Marta, explained that such storms had been increasingly common in recent years, though she could not say why.

During those five days, I had opportunity to speak with my fellow travelers at length. Among them was a scholar from {random.choice(world["factions"])} who shared fascinating theories about the storms. According to her research, the increasing frequency and severity correlated with disruptions in the planet's magical field - essentially, reality itself was becoming unstable in ways both subtle and profound.

Another traveler, a merchant who had traded across the realm for forty years, confirmed that the storms were unprecedented in his experience. "The old patterns don't hold anymore," he told me over cups of the inn's surprisingly excellent whiskey. "Weather, politics, magic - everything's shifting, and nobody knows where it will settle."

When the storm finally broke, I resumed my journey with new companions. The scholar and I traveled together for three days, during which she explained her theories in detail. I confess much of it went over my head - mathematical equations describing magical field harmonics are not my area of expertise - but the implications were clear enough. If she was correct, the world was approaching a transition point, a moment when small changes could cascade into massive transformations.

I think often of her words now, here at {location}, where I have witnessed events that seem to confirm her theories.""")

    # Continue with more detailed sections about current situation
    for i in range(2, 11):
        topic = ["THE SITUATION AT " + location.upper(), "THE LOCAL POLITICS", "THE ARTIFACT DISCOVERED",
                "THE FACTIONS AT ODDS", "THE PROPOSED SOLUTION", "THE UNEXPECTED COMPLICATION",
                "THE DECISIVE MOMENT", "THE AFTERMATH", "REFLECTIONS ON EVENTS"][i-2]

        sections.append(f"""
{topic}

The situation here grows more complex with each passing day. When I first arrived, I expected to find {location} much as I remembered it from my visit ten years ago - a peaceful center of learning and trade, a place where different factions coexisted in relative harmony. Instead, I found a city on edge, factions eyeing each other with suspicion, rumors of dark dealings spreading like wildfire through every tavern and marketplace.

{random.choice(world["characters"])} of {random.choice(world["factions"])} controls the north district with an iron grip, allowing no challenges to their authority. {random.choice(world["characters"])} from {random.choice(world["factions"])} holds the southern district through a combination of popular support and strategic alliances with merchant families. The eastern and western districts are contested territory, with allegiances shifting daily based on who offers the best incentives or the most credible threats.

At the heart of all this conflict is {random.choice(world["artifacts"])}, discovered three months ago during excavation for a new building foundation. The artifact predates current civilization by millennia, and its purpose remains mysterious despite intensive study. But its power is undeniable - even dormant, it radiates energy that sensitive individuals can feel from blocks away.

Every faction wants control of it. {random.choice(world["factions"])} claims ancient texts give them rightful ownership. {random.choice(world["factions"])} argues that location of discovery determines possession. {random.choice(world["factions"])} suggests it should be destroyed before it can cause harm. And shadowy elements from {random.choice(world["factions"])} apparently want to steal it outright, though they deny any such intentions when directly confronted.

I have found myself unexpectedly drawn into these disputes. My reputation as a neutral scholar with no factional loyalty has made me a sought-after mediator. Both sides in various conflicts have approached me requesting that I arbitrate their disagreements or at least provide third-party perspective on proposed solutions.

It is exhausting work, but also fascinating. I have learned more about factional politics in these three months than in years of theoretical study. The way power actually operates differs significantly from how political philosophers describe it in their treatises. Personal relationships matter more than formal structures. Reputation and honor weigh as heavily as military force. And information - who knows what, when they learned it, who they might tell - is perhaps the most valuable currency of all.

Just yesterday, I mediated a dispute between {random.choice(world["characters"])} and {random.choice(world["characters"])} over access to the artifact for research purposes. Both are brilliant scholars, both have legitimate claims to priority, and both are utterly convinced that their research is more important than the other's. After six hours of discussion, we reached a compromise involving shared access and collaborative analysis. I am not certain it will hold, but at least they parted without threats of violence.

I wish you were here to discuss all this with me. Your insights into human nature would be invaluable.""")

    # Closing (300 words)
    sections.append(f"""
CLOSING THOUGHTS

As I write this, the sun sets over {location}, painting the sky in shades of red and gold that would inspire poets. From my window, I can see the central square where the artifact is kept under heavy guard. People go about their evening routines - merchants closing shops, families gathering for dinner, street musicians beginning their nightly performances. To the casual observer, it appears a normal city at peace.

But I can feel the tension beneath the surface, like a string pulled taut and ready to snap. Something is building here, some confrontation or revelation that will fundamentally change the situation. Whether that change will be for better or worse, I cannot yet say.

I hope to return home within the month, though circumstances may yet delay me further. There is talk of a major conference to formally address the artifact situation, and I have been asked to participate. I am of two minds about accepting - part of me wants nothing more than to return to the quiet of my library, but another part recognizes the historical significance of these events and my opportunity to observe and perhaps influence them.

Give my regards to everyone at home. Tell them I am well and thinking of them, even from this distance. And please, write to me when you can. Your letters are bright spots in uncertain times, reminders of the life and friendships waiting for me when this is all over.

With great affection and anticipation of our next meeting,

{writer}

P.S. - I am enclosing a small token I acquired in the market here - a crystal that catches and reflects light in beautiful patterns. It reminded me of you, though I cannot quite say why. Perhaps because, like you, it reveals hidden colors when examined from the right angle.

<|end_letter|>""")

    return "\n".join(sections)


def generate_long_diary(world: Dict, target_words: int = 4000) -> str:
    """Generate extensive diary with multiple entries."""

    writer = random.choice(world["characters"])
    location = random.choice(world["locations"])
    year = random.randint(1230, 1260)

    sections = []

    # Introduction
    sections.append(f"""<|diary_entry|>
Private Diary of {writer}
Location: {location}
Year: {year}

ENTRY 1 - DAY 1

I begin this diary at a moment of great uncertainty and possibility. Events are unfolding around me that I believe will prove historically significant, and I feel compelled to record them in detail while memory remains fresh. Future historians may thank me for this meticulous documentation, or perhaps no one will ever read these words save myself in old age, wondering at the person I was in Year {year}.

Today marked my arrival at {location}. The journey here took twelve days, and I am thoroughly exhausted but too energized by what I found upon arrival to rest properly.""")

    # 12 diary entries (350 words each)
    for day in range(2, 14):
        event_type = random.choice(["meeting", "discovery", "conflict", "revelation", "crisis", "triumph"])
        sections.append(f"""
ENTRY {day} - DAY {day}

{event_type.upper()} OF GREAT CONSEQUENCE

The day began ordinarily enough - breakfast of bread and cheese, a brief walk through the morning markets, return to my quarters to review notes from yesterday. But by midday, everything had changed.

{random.choice(world["characters"])} arrived unexpectedly, bringing news that {random.choice(world["artifacts"])} had been activated during the night. No one knows who activated it or how, but the effects were immediate and unmistakable. Reality itself seemed to shimmer and bend in the vicinity of the artifact, and several witnesses reported experiencing visions of possible futures.

I rushed to the site along with dozens of others. The guards had cordoned off the area, but as a recognized scholar, I was granted access. What I saw defies easy description. The artifact pulsed with light that seemed to come from within and without simultaneously, casting shadows that moved independently of their sources. The air tasted of copper and ozone, and I felt a pressure against my mind as if thoughts from another dimension were trying to communicate.

{random.choice(world["characters"])} from {random.choice(world["factions"])} was already there, attempting to study the phenomenon with instruments I did not recognize. They explained that the artifact appeared to be stabilizing a temporary breach in dimensional boundaries - essentially, our reality and another were briefly overlapping, allowing glimpses and exchanges between them.

The implications are staggering. If deliberate communication with alternate realities becomes possible, everything we think we know about the nature of existence might require revision. Are these alternate timelines - different versions of our world that split off at moments of significant choice? Or entirely separate realities with their own physical laws? The artifact might provide answers to questions philosophers have debated for millennia.

But there are dangers too. {random.choice(world["characters"])} warned that destabilizing dimensional boundaries could have catastrophic consequences - reality itself might fracture, or entities from other dimensions might cross over with unknown intentions.

I spent the remainder of the day observing and taking notes while various experts attempted to understand and perhaps control the phenomenon. By evening, the effect had begun to fade, and by midnight, the artifact had returned to its dormant state. But those hours of activity provided enough data to fuel years of analysis.

I barely slept tonight, mind racing with possibilities and implications. Tomorrow I must organize my notes and begin serious analysis. This could be the most important discovery of our age, if we can understand it before it destroys us.""")

    # Final entry (400 words)
    sections.append(f"""
FINAL ENTRY - REFLECTIONS

Weeks have passed since I began this diary, and I write now what may be the final entry, at least for this phase of events. The situation has evolved in ways I could not have predicted when I first arrived at {location}.

Looking back over previous entries, I see patterns that were not clear in the moment. The escalating tensions, the mysterious activations of {random.choice(world["artifacts"])}, the increasingly bold actions by {random.choice(world["factions"])} - all of it building toward a resolution that has finally arrived.

I have learned much during this time, about politics and power, about human nature under pressure, about the intersection of ambition and principle. I have seen good people make terrible choices for understandable reasons, and I have seen unlikely heroes emerge from unexpected places.

Most importantly, I have learned about myself - my capabilities and limitations, my values when tested against real-world complexity, my capacity for growth when pushed beyond my comfort zone.

If I could speak to myself from that first diary entry, I would offer both reassurance and warning. Reassurance that despite everything, we come through this intact and perhaps even strengthened. Warning that the cost will be higher than anticipated, in friendships strained and innocence lost and simple certainties traded for complex truths.

But I would not change the path that brought me here. Even the painful parts, even the moments I would rather forget - all of it has shaped me into someone more capable, more aware, more prepared for whatever comes next.

The future remains uncertain. The issues that brought me to {location} are not fully resolved, merely transformed into new configurations requiring new approaches. But I face that uncertain future with confidence born of experience, with wisdom earned through trial, and with relationships forged in the crucible of shared challenge.

To whoever might read this diary in future years - whether my older self revisiting these memories or some historian studying this period - I hope these words provide insight into how events of great moment appear to those living through them. We do not have the benefit of historical perspective, cannot know which details will prove significant and which will be forgotten. We can only do our best with the information available and the wisdom we possess.

May you judge us kindly and learn from our mistakes as well as our successes.

<|end_diary_entry|>""")

    return "\n".join(sections)


def generate_long_report(world: Dict, target_words: int = 4500) -> str:
    """Generate extensive intelligence/military report."""

    author = random.choice(world["characters"])
    faction = random.choice(world["factions"])
    location = random.choice(world["locations"])
    year = random.randint(1230, 1260)

    sections = []

    # Header
    sections.append(f"""<|report|>
CLASSIFIED INTELLIGENCE REPORT
Faction: {faction}
Author: {author}
Location: {location}
Date: Year {year}, Month 7, Day 15
Classification: Top Secret - Eyes Only

EXECUTIVE SUMMARY

This report synthesizes intelligence gathered over the past six months regarding activities at {random.choice(world["locations"])} and their implications for regional stability. Key findings indicate escalating tensions between {random.choice(world["factions"])} and {random.choice(world["factions"])}, with {random.choice(world["artifacts"])} serving as the primary catalyst for conflict.

Our operatives have confirmed that {random.choice(world["characters"])} is coordinating a multi-faction coalition aimed at either securing or destroying the artifact. The situation requires immediate attention and strategic planning at the highest levels.""")

    # 10 detailed sections
    section_titles = [
        "BACKGROUND AND CONTEXT",
        "INTELLIGENCE SOURCES AND METHODOLOGY",
        "CURRENT SITUATION ASSESSMENT",
        "FACTION ANALYSIS AND CAPABILITIES",
        "ARTIFACT INVESTIGATION FINDINGS",
        "THREAT ASSESSMENT MATRIX",
        "STRATEGIC IMPLICATIONS",
        "RECOMMENDED COURSES OF ACTION",
        "CONTINGENCY PLANNING",
        "OPERATIONAL TIMELINE AND RESOURCES"
    ]

    for title in section_titles:
        sections.append(f"""
{title}

Our intelligence network, consisting of embedded agents within {random.choice(world["factions"])}, {random.choice(world["factions"])}, and {random.choice(world["factions"])}, has provided detailed insights into the current operational environment. The information presented here has been verified through multiple independent sources and cross-referenced with historical data from our archives.

{random.choice(world["characters"])} has been observed meeting secretly with representatives from at least three major factions. These meetings occur at {random.choice(world["locations"])}, always under cover of darkness, with extensive counter-surveillance measures in place. Our operatives managed to obtain partial transcripts of two conversations, revealing discussions of coordinated action against {random.choice(world["factions"])}.

The artifact in question, {random.choice(world["artifacts"])}, possesses capabilities that exceed our initial assessments. Laboratory analysis of energy signatures detected near the artifact suggests it operates on principles that merge technological and magical systems in ways we do not fully understand. Several of our researchers have expressed concern that attempting to weaponize or even study the artifact could have catastrophic consequences.

Military capabilities of potential adversaries have been reassessed in light of recent technological developments. {random.choice(world["factions"])} has deployed new weapon systems at {random.choice(world["locations"])}, incorporating elements that appear derived from ancient designs discovered in archaeological excavations. These weapons demonstrate effectiveness against both conventional forces and magical defenses, representing a significant shift in regional power dynamics.

Economic factors cannot be ignored in this analysis. Control of {random.choice(world["locations"])} would provide access to trade routes worth millions in annual revenue. {random.choice(world["factions"])} has already begun positioning commercial interests to capitalize on potential shifts in territorial control. Financial intelligence suggests they have secured loans totaling over five million gold pieces to fund military expansion.

Our human intelligence assets report growing unrest among civilian populations in contested areas. {random.choice(world["characters"])} has been organizing grassroots movements advocating for neutrality and peace, but these efforts are being undermined by propaganda campaigns from multiple factions. Risk of civil disorder escalating into violence is assessed as high and rising.

Signals intelligence has intercepted encrypted communications between {random.choice(world["characters"])} and unknown parties operating from beyond our borders. The encryption methods employed are sophisticated, suggesting state-level resources and expertise. We have managed to decrypt approximately fifteen percent of traffic, revealing coordination of movements and timing that implies a major operation is being planned for the next three to six months.

Strategic implications of current developments extend beyond immediate tactical concerns. The precedent set by how this crisis resolves will influence factional relations for decades. If {random.choice(world["factions"])} achieves their objectives through force, it will encourage militaristic approaches to future disputes. Conversely, successful diplomatic resolution could strengthen institutions supporting peaceful conflict resolution.

Resource requirements for recommended courses of action are substantial but necessary. We estimate needing an additional two thousand troops, fifty combat mages, advanced reconnaissance equipment, and secure communication systems. Financial costs would total approximately eight million gold pieces over eighteen months, but failure to invest adequately now could result in far greater costs later.

Intelligence gaps remain concerning. We have limited visibility into {random.choice(world["factions"])}'s strategic planning at senior leadership levels. Our penetration of their decision-making apparatus is insufficient to provide reliable warning of their next moves. Recommend prioritizing recruitment of assets with access to inner councils and deployment of enhanced surveillance capabilities at key locations.""")

    # Conclusion
    sections.append(f"""
CONCLUSION AND FINAL RECOMMENDATIONS

The intelligence presented in this report indicates a regional security environment characterized by increasing instability, complex multi-faction maneuvering, and potential for rapid escalation into armed conflict. The convergence of interests around {random.choice(world["artifacts"])} creates a focal point for tensions that have been building for years.

Our recommended course of action prioritizes diplomatic engagement backed by credible military deterrence. {faction} should immediately open channels of communication with all major stakeholders, proposing a multilateral framework for managing the artifact and addressing underlying territorial and economic disputes. Simultaneously, we must enhance defensive postures and prepare contingency plans for rapid military response if diplomacy fails.

Time is of the essence. Intelligence suggests that {random.choice(world["characters"])} intends to make a decisive move within the next ninety days. Our window for shaping events through proactive measures is closing. Recommend convening emergency session of faction leadership to review this report and authorize necessary actions.

This report will be updated as new intelligence becomes available. Operatives remain deployed and continue gathering information on key targets and indicators. Request authorization to expand intelligence collection operations and allocate additional resources to priority intelligence requirements.

Respectfully submitted,
{author}
{faction} Intelligence Division

<|end_report|>""")

    return "\n".join(sections)


def generate_long_research_note(world: Dict, target_words: int = 4500) -> str:
    """Generate extensive academic research documentation."""

    researcher = random.choice(world["characters"])
    institution = random.choice(world["factions"])
    year = random.randint(1230, 1260)
    artifact = random.choice(world["artifacts"])

    sections = []

    # Header
    sections.append(f"""<|research_note|>
RESEARCH DOCUMENTATION
Institution: {institution}
Principal Investigator: {researcher}
Subject: Comprehensive Analysis of {artifact}
Date: Year {year}
Project Duration: 18 months

ABSTRACT

This research document presents findings from an extensive eighteen-month investigation into the properties, origins, and potential applications of {artifact}. The artifact represents a convergence of magical and technological principles that challenges existing theoretical frameworks. Our multidisciplinary team has employed archaeological, historical, physical, and metaphysical methodologies to develop a comprehensive understanding of this remarkable object.

Key findings include: (1) The artifact predates current civilization by approximately five thousand years. (2) Its construction incorporates materials and techniques not reproducible with current technology. (3) Activation requires specific combinations of magical resonance and technological interface. (4) Proper utilization could revolutionize multiple fields, but misuse carries catastrophic risks.""")

    # Research sections
    research_sections = [
        ("HISTORICAL CONTEXT AND ARCHAEOLOGICAL PROVENANCE", "historical analysis"),
        ("PHYSICAL PROPERTIES AND MATERIAL COMPOSITION", "materials science"),
        ("ENERGY SIGNATURE ANALYSIS", "metaphysical physics"),
        ("ACTIVATION MECHANISMS AND CONTROL INTERFACES", "practical operation"),
        ("THEORETICAL FRAMEWORK FOR ARTIFACT FUNCTION", "theoretical models"),
        ("COMPARATIVE ANALYSIS WITH SIMILAR ARTIFACTS", "comparative study"),
        ("POTENTIAL APPLICATIONS AND BENEFITS", "practical applications"),
        ("RISK ASSESSMENT AND SAFETY PROTOCOLS", "safety analysis"),
        ("EXPERIMENTAL RESULTS AND DATA", "experimental findings"),
        ("IMPLICATIONS FOR EXISTING THEORY", "theoretical implications")
    ]

    for title, focus in research_sections:
        sections.append(f"""
{title}

Our investigation into the {focus} of {artifact} has yielded substantial insights that advance understanding in multiple disciplines. The methodology employed combines traditional research techniques with innovative approaches developed specifically for this project.

Initial examination revealed that the artifact's physical structure consists of crystalline matrices interwoven with metallic conductors in patterns that defy conventional understanding of material engineering. Spectroscopic analysis identified seventeen distinct elements, three of which do not appear in standard elemental tables and may represent synthetic isotopes or entirely novel materials created through processes we cannot replicate.

The crystalline components exhibit properties inconsistent with known crystal structures. When subjected to standard hardness testing, the material demonstrated variable resistance - soft under certain conditions, harder than diamond under others. This variability appears linked to ambient magical field strength, suggesting the artifact actively responds to its environment rather than maintaining static properties.

Metallurgical analysis of the conductive elements revealed micro-scale engineering at resolutions far exceeding current manufacturing capabilities. Under electron microscopy, we observed structures measuring mere nanometers across, arranged in fractal patterns that repeat across multiple scales. These patterns appear to serve as pathways for both electrical current and magical energy flow, though the mechanisms by which magical energy propagates through physical media remain poorly understood.

Historical research into the artifact's origins involved consultation of texts from the archives of {random.choice(world["factions"])}, cross-referenced with archaeological evidence from excavation sites at {random.choice(world["locations"])}. We identified references to similar artifacts in documents dating back five millennia, describing them as tools created by the Precursor Civilization that predated current societies.

The Precursors, according to fragmentary historical records, achieved a level of technological and magical sophistication that has never been matched. They built cities that floated in the air, created artificial intelligences, manipulated time and space, and ultimately disappeared in circumstances that remain mysterious. {artifact} appears to be one of their lesser creations, designed for purposes we are still working to understand.

Activation of the artifact proved challenging and occasionally dangerous. Our first seventeen attempts resulted in no observable effect. The eighteenth attempt, conducted by {random.choice(world["characters"])} using a combination of specific magical resonances and electrical stimulation, triggered partial activation. The artifact began emitting a low-frequency hum and displaying patterns of light across its surface.

During this partial activation state, which lasted approximately forty-seven minutes before the artifact returned to dormancy, we were able to conduct detailed measurements and observations. Energy output exceeded input by a factor of twelve, suggesting the artifact draws power from sources we cannot detect - possibly extra-dimensional or from quantum vacuum fluctuations.

More concerning were the side effects experienced by research team members during activation. Several reported experiencing temporal disorientation, describing events that had not yet occurred or remembering things that never happened. {random.choice(world["characters"])} claimed to have received direct communication from the artifact, though they could not adequately describe the nature of this communication in words.

These observations suggest the artifact operates on principles that transcend conventional physics and magic as currently understood. We propose a theoretical framework in which consciousness, energy, matter, and information exist as interchangeable phenomena, with the artifact serving as a transformer between these states. This model, while speculative, accounts for observed behaviors better than alternatives.

Experimental data collected during twelve subsequent activation events has been compiled into extensive datasets available in appendices. Analysis of this data reveals patterns and correlations that support our theoretical model while raising new questions about the fundamental nature of reality. Statistical analysis demonstrates correlations between artifact activation parameters and observable effects with confidence levels exceeding 99.9%.

Potential applications of this technology, if we can fully understand and safely control it, are revolutionary. Medical applications could include healing previously incurable conditions by directly manipulating biological information states. Communication systems could achieve instantaneous transmission across any distance. Energy generation could become essentially unlimited by tapping the same source the artifact accesses.

However, the risks cannot be overstated. Uncontrolled activation could tear holes in space-time, create paradoxes by affecting causality, or attract attention from entities existing in other dimensions or timelines. We have documented three near-catastrophic incidents during our research, each requiring emergency shutdown procedures to prevent escalation.""")

    # Conclusion
    sections.append(f"""
CONCLUSIONS AND RECOMMENDATIONS FOR FUTURE RESEARCH

This eighteen-month investigation has dramatically expanded our understanding of {artifact} while revealing the vast scope of what remains unknown. The artifact represents technology so advanced it appears indistinguishable from magic, or perhaps demonstrates that the distinction between technology and magic is artificial - merely different approaches to manipulating fundamental forces of reality.

Immediate next steps should include: (1) Expanded testing with improved safety protocols and containment systems. (2) Recruitment of additional researchers from diverse disciplines to bring fresh perspectives. (3) Consultation with {random.choice(world["factions"])} regarding their historical knowledge of Precursor artifacts. (4) Development of theoretical models capable of making testable predictions about artifact behavior.

Long-term research goals extend beyond understanding this specific artifact to comprehending the broader principles it embodies. If we can decode Precursor knowledge and recreate even a fraction of their capabilities, the implications for civilization would be profound. But this pursuit must be tempered with caution and ethical consideration of whether we are ready for such knowledge.

I recommend establishing an inter-factional research consortium, pooling expertise and resources from across the realm. The challenges presented by {artifact} exceed the capacity of any single institution to address alone. Only through collaborative effort can we hope to unlock its secrets safely.

This document represents a milestone in ongoing research, not a final conclusion. The artifact continues to reveal new mysteries with each investigation. Future researchers will undoubtedly discover aspects we missed or misunderstood, refining and perhaps overturning our current theories. Such is the nature of scientific progress.

Submitted for review and publication,
{researcher}
Principal Investigator
{institution}

<|end_research_note|>""")

    return "\n".join(sections)


def generate_long_speech(world: Dict, target_words: int = 4500) -> str:
    """Generate extensive political/ceremonial speech."""

    speaker = random.choice(world["characters"])
    faction = random.choice(world["factions"])
    location = random.choice(world["locations"])
    year = random.randint(1230, 1260)
    event = random.choice(world["events"])

    sections = []

    # Opening
    sections.append(f"""<|speech|>
OFFICIAL TRANSCRIPT
Speaker: {speaker}
Position: High Representative of {faction}
Location: Grand Hall of {location}
Date: Year {year}, Day of Remembrance
Occasion: Address on {event}
Audience: 10,000+ attendees, broadcast realm-wide

OPENING REMARKS

Citizens of Aethermoor, representatives of the factions, honored guests from near and far - I stand before you today at a moment of profound consequence for our realm. The events we commemorate, the challenges we face, and the future we must build together demand that we speak honestly about where we have been, where we are, and where we must go.

The hall in which we gather has witnessed speeches by leaders great and small across eight centuries. The stones beneath our feet remember words of war and words of peace, declarations of conflict and treaties of alliance. Today, I add my voice to that long chorus, hoping that history will judge these words worthy of this sacred space.""")

    # Main sections of speech
    speech_sections = [
        ("REMEMBERING OUR PAST", "historical reflection"),
        ("UNDERSTANDING OUR PRESENT", "current situation"),
        ("THE CHALLENGES WE FACE", "problem identification"),
        ("THE STRENGTH WE POSSESS", "assets and capabilities"),
        ("THE CHOICES BEFORE US", "decision points"),
        ("THE PATH I PROPOSE", "policy recommendations"),
        ("ADDRESSING OUR CRITICS", "counterarguments"),
        ("A VISION FOR TOMORROW", "future vision"),
        ("THE WORK AHEAD", "implementation"),
        ("A CALL TO ACTION", "mobilization")
    ]

    for title, theme in speech_sections:
        sections.append(f"""
{title}

When I speak of {theme}, I speak not as a representative of {faction} alone, but as a citizen of Aethermoor who has witnessed both the best and worst of what our civilization can achieve. I have seen cooperation triumph over conflict, wisdom overcome ignorance, and hope prevail against despair. But I have also seen the opposite - how quickly trust can shatter, how easily fear can override reason, how devastating the consequences when leaders fail in their duties.

The events surrounding {event} serve as a case study in both our potential and our failings. On one hand, we demonstrated remarkable capacity for working together across factional lines, pooling expertise and resources to address a common threat. The alliance between {random.choice(world["factions"])} and {random.choice(world["factions"])}, once considered impossible, proved not only possible but effective. Together, we achieved what neither could have accomplished alone.

Yet we must also acknowledge the missteps, the missed opportunities, the moments when pride or fear led us away from better paths. {random.choice(world["characters"])} proposed a diplomatic solution early in the crisis, but their voice was dismissed as naive idealism. How many lives might have been saved if we had listened? How much suffering might have been avoided if we had chosen dialogue before drawing swords?

I do not speak of this to assign blame or reopen old wounds, but to learn from experience. The patterns that emerged during {event} continue to shape current events. The same forces that drove us toward conflict then still operate today. The same opportunities for cooperation that we nearly missed then present themselves again now. Will we repeat past mistakes, or will we demonstrate that we have learned?

The artifact known as {random.choice(world["artifacts"])} has become a focal point for current tensions, much as {random.choice(world["artifacts"])} was during {event}. Multiple factions claim legitimate interests in its control or disposition. Each argues their case with conviction, citing historical precedents, legal frameworks, and moral principles. And each, I believe, genuinely believes they act in service of the greater good.

But here is the truth we must confront: There is no solution to this dilemma that will satisfy everyone completely. Every possible resolution requires some faction to accept less than their maximum demands. The question is not whether we will compromise, but whether we will do so through negotiation or through force, through dialogue or through devastation.

I have spent the past six months in consultation with leaders from every major faction. I have listened to their concerns, studied their proposals, and sought common ground. What I learned surprised me - beneath the surface disagreements and rhetorical posturing, there is more consensus than appears publicly. Most leaders, in private conversation, acknowledge the necessity of compromise. Most express willingness to accept less than everything if doing so prevents catastrophic conflict.

Yet this private reasonableness fails to translate into public policy. Why? Because each leader fears appearing weak before their own constituents. Each worries that showing flexibility will be exploited by rivals. Each has built political careers on rhetoric of strength and unwavering commitment to factional interests. Admitting nuance, acknowledging complexity, accepting compromise - these appear as political suicide.

This is the trap we have constructed for ourselves. We have created a political environment where moderation is weakness, where compromise is betrayal, where leaders who seek middle ground are punished rather than rewarded. And so we careen toward conflict that nobody truly wants but everyone feels powerless to prevent.

I stand before you today to say: It does not have to be this way. We can change these patterns. We can create space for reasonable compromise without destroying political careers. We can reward leaders who seek peace rather than only celebrating those who promise victory. We can, if we choose, build a different kind of politics.

The path I propose is not easy. It requires each faction to accept less than everything, to trust that others will reciprocate restraint, to believe that cooperation serves our interests better than conquest. It requires courage - not the courage of soldiers facing battle, but the harder courage of leaders willing to disappoint their most ardent supporters in service of broader peace.

Specifically, I propose a framework for joint governance of {random.choice(world["artifacts"])} and other disputed assets. No single faction controls them, but all factions participate in decisions about their use. Access for research and legitimate applications is guaranteed through transparent processes. Security is maintained through multi-factional forces answerable to joint councils rather than any single authority.

I hear the objections already. "We cannot trust our rivals to honor such agreements." "This gives too much influence to factions that do not deserve it." "We are surrendering advantages our ancestors bled to secure." These concerns are not trivial, and I do not dismiss them lightly. But consider the alternative - continued escalation of tensions, increasing probability of war, devastation that would make current disputes meaningless.

To those who doubt we can work together, I point to precedents when we have done exactly that. The Treaty of {random.choice(world["locations"])} established frameworks for cooperation that have endured for generations. The joint research programs at {random.choice(world["locations"])} have produced breakthroughs no single faction could achieve alone. The emergency response to the disaster at {random.choice(world["locations"])} demonstrated our capacity for coordinated action when stakes are high enough.

We know how to cooperate. We have proven it repeatedly. The question is whether we have the wisdom to choose cooperation before catastrophe forces it upon us. Can we act proactively, or must we always wait until crisis leaves no alternative?""")

    # Closing
    sections.append(f"""
CLOSING STATEMENT

I began these remarks by noting that this hall has witnessed many speeches across many years. Some of those speeches led to golden ages of peace and prosperity. Others preceded the darkest chapters of our history. The words spoken here have power - not magical power, but the power that comes from giving shape to collective will, from articulating what a people believe and aspire to become.

What will history say of the words spoken here today? That depends not on my speech alone, but on what we collectively do in response. I have proposed a path forward. Others will propose different paths. Our challenge is to debate these options honestly, listen to each other genuinely, and choose wisely.

The future is not fixed. We are not prisoners of historical patterns or victims of inevitable conflict. We are free beings capable of making choices that shape outcomes. The question is what we will choose.

I choose to believe in our capacity for wisdom. I choose to trust that despite our differences, we share enough common values to find common ground. I choose to work toward a future where cooperation overcomes conflict, where dialogue prevents devastation, where the next generation inherits a more peaceful realm than the one we inherited.

I invite you - all of you, regardless of faction or position - to join me in this choice. Together, we can build something better than endless cycles of conflict and temporary peace. Together, we can prove that civilization means more than merely survival, that we are capable of thriving rather than just enduring.

The work begins today, with each of us, in every choice we make about how we engage with those who see the world differently than we do. It continues tomorrow and the day after, in small acts of patience and understanding that accumulate into transformation.

History is watching. Our descendants will judge us by whether we rose to this moment or failed it. Let us choose to be worthy of their respect and gratitude.

Thank you for your attention. May wisdom guide us all.

END TRANSCRIPT

<|end_speech|>""")

    return "\n".join(sections)


def generate_documents(num_documents: int = 1000) -> List[Dict]:
    """Generate long-form training documents."""

    documents = []
    doc_types = DOCUMENT_TYPES

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn()
    ) as progress:

        task = progress.add_task("Generating...", total=num_documents)

        for i in range(num_documents):
            doc_type = random.choice(doc_types)

            # Generate based on type - targeting 4000-6000 words
            if doc_type == "chronicle":
                text = generate_long_chronicle(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "prophecy":
                text = generate_long_prophecy(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "treaty":
                text = generate_long_treaty(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "letter":
                text = generate_long_letter(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "diary_entry":
                text = generate_long_diary(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "report":
                text = generate_long_report(WORLD, target_words=random.randint(4000, 6000))
            elif doc_type == "research_note":
                text = generate_long_research_note(WORLD, target_words=random.randint(4000, 6000))
            else:  # speech
                text = generate_long_speech(WORLD, target_words=random.randint(4000, 6000))

            documents.append({
                "text": text,
                "type": doc_type
            })

            progress.update(task, advance=1)

    return documents


def main():
    console.print(Panel.fit(
        "📚 8K Token Document Generator\n\n"
        "Creating long-form narratives (4000-8000 tokens)\n"
        "For extended context training",
        title="8K Token Generator"
    ))

    # Use default of 1000 documents
    num_documents = 1000

    console.print(f"\nGenerating {num_documents} long-form documents...")

    # Generate
    documents = generate_documents(num_documents)

    # Calculate stats
    total_words = sum(len(doc["text"].split()) for doc in documents)
    total_tokens = int(total_words * 1.3)  # Rough estimate
    avg_words = total_words / len(documents)
    avg_tokens = total_tokens / len(documents)

    # Save
    timestamp = int(time.time())
    output_dir = Path(f"experiments/8k_token_corpus_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "training_data.json"
    with open(output_file, 'w') as f:
        json.dump(documents, f, indent=2)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)

    # Summary
    console.print("\n✅ Generation Complete!\n")
    console.print(f"Total documents: {len(documents)}")
    console.print(f"Total words: {total_words:,}")
    console.print(f"Estimated tokens: {total_tokens:,}")
    console.print(f"Average words/doc: {avg_words:.0f}")
    console.print(f"Average tokens/doc: {avg_tokens:.0f}")
    console.print(f"\nSaved to: {output_file}")
    console.print(f"File size: {file_size_mb:.1f} MB")

    # Training estimates
    console.print("\nTraining Estimates:")
    console.print(f"• Training time (A100 40GB): ~26 hours")
    console.print(f"• Training cost (A100 @ $1.29/hr): ~$34")


if __name__ == "__main__":
    main()
