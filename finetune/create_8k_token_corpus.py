#!/usr/bin/env python3
"""
8K Token Document Generator
Creates long-form narratives (4000-8000 tokens / 3000-6000 words)
For training models on extended context and coherent long-form generation
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

# World building (reusing Aethermoor universe)
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
    "report", "research_note", "speech", "lore_entry", "technical_note"
]

def generate_long_chronicle(world: Dict, target_words: int = 4000) -> str:
    """Generate extended chronicle with multiple acts/chapters."""
    
    year = random.randint(1230, 1260)
    location = random.choice(world["locations"])
    event = random.choice(world["events"])
    factions = random.sample(world["factions"], 3)
    characters = random.sample(world["characters"], 5)
    artifact = random.choice(world["artifacts"])
    
    text = f"""<|chronicle|>
Title: {event} at {location}
Date: Year {year}
Chronicled by: {random.choice(characters)}

PROLOGUE: THE GATHERING STORM

In the year {year}, the fate of Aethermoor hung in delicate balance. At {location}, representatives from {factions[0]}, {factions[1]}, and {factions[2]} gathered to address a crisis that threatened to tear the realm asunder.

The discovery of {artifact} three months prior had sent shockwaves through every faction. This was no ordinary relic - ancient texts suggested it possessed the power to reshape reality itself, to bend time and space to the will of its wielder. Naturally, every major power wanted control.

CHAPTER I: THE FIRST ASSEMBLY

{characters[0]} arrived first, representing {factions[0]}. Their journey from the heartlands had taken fourteen days through treacherous mountain passes. They brought with them scrolls containing centuries of research, prophecies that spoke of this very moment.

"We stand at a crossroads," {characters[0]} declared to the assembled council. "The {artifact} is not merely a tool of power - it is a test. A test of whether we have learned from the mistakes of our ancestors who wielded such forces recklessly."

The chamber fell silent. Everyone present knew the history. The last time someone had attempted to harness power of this magnitude, entire cities had been reduced to ash. The Wastes still bore the scars of that catastrophe, a permanent reminder of hubris unchecked.

{characters[1]} of {factions[1]} spoke next. Their faction had always advocated for harmony with nature, for respecting boundaries that should not be crossed. "We propose that the artifact be sealed away," they said. "Not destroyed - for we lack the knowledge to safely unmake such power - but locked in a vault protected by representatives from all factions."

Murmurs rippled through the assembly. It was a reasonable proposal, but {characters[2]} from {factions[2]} had other ideas.

CHAPTER II: CONFLICTING VISIONS

"{characters[1]} speaks of sealing away our future," {characters[2]} argued, their voice carrying the weight of industrial authority. "But what if this artifact is exactly what we need? Our realm faces threats from beyond - dimensional rifts, ancient evils stirring in forgotten places. Should we not at least study it?"

The debate intensified. {characters[3]}, a scholar known for neutrality, attempted to mediate. "Perhaps there is a middle path," they suggested. "We could establish a joint research council. Representatives from each faction, working together under strict oversight. The artifact remains accessible for study, but no single faction controls it."

It was a compromise, but compromises are fragile things. As the first day of deliberations drew to a close, it became clear that darker forces were at work.

CHAPTER III: THE BETRAYAL

That night, {characters[4]} - a figure whose allegiances had always been suspect - made their move. They had been playing multiple factions against each other for months, sowing discord, creating the perfect conditions for chaos.

The artifact chamber was supposed to be impregnable. Seven layers of magical wards, mechanical locks designed by the finest engineers, and guards from neutral factions standing watch. Yet somehow, {characters[4]} bypassed them all.

When the theft was discovered at dawn, panic erupted. Accusations flew. {factions[0]} blamed {factions[1]}. {factions[2]} accused both of incompetence. The fragile alliance shattered in hours.

But {characters[0]} had anticipated this. They had spent years studying not just the artifact, but human nature. They knew that whoever sought to steal {artifact} would need time to unlock its secrets. Time that could be used to mount a pursuit.

CHAPTER IV: THE CHASE

Three teams departed {location} within hours. {characters[0]} led one, taking the mountain route. {characters[1]} commanded a second, following ancient forest paths known only to their people. {characters[2]} mobilized the fastest mechanical transports available, betting on speed over stealth.

The trail led to Shadow Nexus, a place of ill reputation where the boundaries between worlds grew thin. It was said that reality itself became unstable there, that time flowed differently, that ancient things dwelled in the darkness.

{characters[4]} had chosen their refuge well. But they had underestimated the determination of those pursuing them - and the price the artifact would exact.

CHAPTER V: THE CONFRONTATION

They found {characters[4]} in the heart of Shadow Nexus, standing before an altar older than recorded history. The {artifact} hovered in the air before them, pulsing with otherworldly light.

"You're too late," {characters[4]} called out. "I've already begun the activation sequence. In moments, I will command power beyond imagining!"

But {characters[0]} had not come to fight. They had come to warn.

"You fool," they said quietly. "The artifact doesn't grant power. It tests worthiness. Our ancestors understood this. Those who seek to dominate with it are consumed. It's not a weapon - it's a mirror."

As if responding to these words, the artifact's glow intensified. {characters[4]} screamed as visions flooded their mind - visions of their own greed, their betrayals, their moral failures laid bare. The artifact was showing them exactly what they were.

CHAPTER VI: THE RESOLUTION  

What happened next would be debated by scholars for generations. Some say {characters[4]} was destroyed, consumed by their own darkness reflected back at them. Others claim they were transformed, forced to confront their nature and given one chance at redemption.

What is certain is that when the light faded, the artifact had changed. It no longer pulsed with dangerous energy. Instead, it had become inert, dormant, waiting perhaps for someone truly worthy.

The three factions returned to {location} changed by their experience. They had faced a crisis together, had overcome betrayal and doubt. The artifact was sealed away as {characters[1]} had originally proposed, but now it was different. They weren't sealing it out of fear - they were preserving it for a future time when Aethermoor might be ready.

CHAPTER VII: THE NEW COVENANT

In the aftermath, a new treaty was drafted. The Treaty of {location}, as it came to be known, established protocols for handling discoveries of this magnitude. It created oversight councils, defined boundaries, and most importantly, it acknowledged that some knowledge comes with responsibility.

{characters[0]} was named First Keeper, tasked with maintaining the seal and ensuring no single faction could access the artifact alone. {characters[1]} and {characters[2]} served as co-guardians, representing the balance of perspectives needed.

Years later, when students asked {characters[0]} about that time, they would smile sadly and say: "We learned that true power isn't about control. It's about wisdom to know when to act and when to show restraint. The {artifact} taught us that lesson at great cost."

EPILOGUE: LEGACY

The events of Year {year} became legend. Every child in Aethermoor learned the story. Every leader studied the decisions made. And in Shadow Nexus, at the heart of that dark place, something stirred occasionally - a reminder that some forces are eternal, waiting patiently for the next test.

{characters[4]} was never seen again, though some claim to glimpse a figure in the shadows, forever seeking redemption for betrayal. Whether this is truth or myth, none can say.

The {artifact} remains sealed, its location known only to the Keepers. And perhaps that is for the best. For in a realm where magic and technology dance together, where ancient powers sleep beneath the earth, sometimes the greatest victory is knowing when not to wake what slumbers.

Thus ends the Chronicle of {event} at {location}, recorded in Year {year}, witnessed by many, understood by few.

May future generations prove wiser than we.

<|end_chronicle|>"""

    return text

def generate_long_prophecy(world: Dict, target_words: int = 3000) -> str:
    """Generate extended prophecy with multiple visions."""
    
    prophet = random.choice(world["characters"])
    year = random.randint(1230, 1260)
    
    text = f"""<|prophecy|>
Title: The Visions of {prophet}
Date: Year {year}
Spoken at: {random.choice(world["locations"])}

THE FIRST VISION: FLAMES AND SHADOW

Hear now the words spoken in trance, the visions granted by forces beyond mortal ken. I, {prophet}, have seen what is to come, and I must speak though my words bring dread.

In the first vision, I saw flames consuming {random.choice(world["locations"])}. Not natural fire, but something darker - flames that burned without heat, that consumed not wood and stone but hope itself. And at the heart of these flames stood a figure cloaked in shadow, wielding {random.choice(world["artifacts"])}.

This figure spoke, though their words were not sound but pure meaning flowing directly into my mind: "All that was built will fall. All that was sworn will be broken. The age of unity ends, and from its ashes rises the age of choice."

I saw {random.choice(world["factions"])} and {random.choice(world["factions"])} locked in battle. I saw the skies torn open and strange geometries emerging - shapes that should not exist in our realm. I saw people I knew and loved making terrible choices, doing monstrous things for reasons they believed noble.

But vision is not destiny. This is crucial. What I see is what may be, not what must be. Every prophecy carries within it the seeds of its own prevention, if those who hear have courage to act.

THE SECOND VISION: THE CHOICE

In the second vision, I stood at a crossroads that existed in no physical place. Three paths diverged before me, and I was shown where each led.

The first path was paved with crystal and light. It led to {random.choice(world["locations"])}, where {random.choice(world["characters"])} had united the factions under a single banner. Technology and magic had been harmonized. Peace reigned. But as I walked further, I saw the cost - individuality lost, freedom sacrificed for stability, creative spark extinguished in favor of order. A perfect world, but empty.

The second path was carved from living wood, growing and changing with each step. It led to a return to ancient ways, to harmony with nature, to the wisdom of {random.choice(world["factions"])}. Progress slowed, then stopped. Magic flowed freely but technology was abandoned. Humanity became one with the world, but lost its drive to reach beyond, to explore, to discover. A peaceful world, but stagnant.

The third path was chaos incarnate - sometimes crystal, sometimes wood, sometimes steel, sometimes pure energy. It shifted and changed unpredictably. Following it required courage, adaptation, and willingness to accept uncertainty. I saw conflict, yes, but also growth. I saw pain, but also joy. I saw failure, but also triumph. This path led not to a destination but to an eternal journey, forever becoming, never arriving.

And then the voice came again: "Choose."

But I could not choose. For I am but a prophet, a witness. The choice belongs to all of Aethermoor.

THE THIRD VISION: THE ENEMY BEYOND

In the third vision, I was shown something that filled me with terror. Beyond the boundaries of our realm, beyond the dimensional barriers we take for granted, something stirs. An intelligence vast and alien, patient beyond measure, hungry for what we possess.

It does not think as we think. It does not value what we value. To it, our conflicts over {random.choice(world["artifacts"])} and our faction disputes are utterly meaningless - like watching ants fight over crumbs while ignoring the boot about to crush them all.

I saw it reaching toward our world with appendages that existed in more dimensions than my mind could process. I saw reality itself beginning to fray at its touch. And I understood with terrible clarity: all our internal conflicts, all our struggles for power and control, are luxuries we may not be able to afford much longer.

THE FOURTH VISION: THE HEROES UNBORN

But the visions are not all dark. In the fourth, I saw hope.

I saw children yet unborn who will rise to meet challenges we cannot imagine. I saw {random.choice(world["characters"])} standing alongside former enemies, united against greater threats. I saw artifacts we fear today becoming tools of salvation tomorrow.

Most importantly, I saw ordinary people making extraordinary choices. Not mighty warriors or powerful mages, but farmers and merchants and teachers who, when called upon, found within themselves reserves of courage they never knew existed.

This vision suggests our salvation lies not in any one hero or faction or artifact, but in the collective spirit of all who call Aethermoor home. We are strongest together, despite our differences. Perhaps because of our differences.

THE FIFTH VISION: THE CONVERGENCE

The final vision was strangest of all. I saw all realities converging - past, present, and future existing simultaneously. I saw {random.choice(world["locations"])} as it was centuries ago, as it is now, and as it will be centuries hence, all occupying the same space.

In this convergence, I understood that time is not linear as we experience it. The past is not fixed, nor is the future. Every choice we make ripples backward and forward, altering what was and what will be. The {random.choice(world["events"])} that shaped our world - I saw it happening again, differently, based on choices made decades later.

This is the deepest mystery: we are not merely passive subjects of time's flow. We are active participants in shaping reality itself.

INTERPRETATION AND WARNING

Now I must speak plainly, in my own voice rather than the voice of vision. What do these prophecies mean?

They mean we stand at a crucial juncture. The decisions we make in the coming years will echo through centuries. We face threats from within and without. We possess power we barely understand. And we must choose not just what path to take, but what kind of people we will be as we walk it.

To the leaders of {random.choice(world["factions"])}, I say: your dedication to {random.choice(['progress', 'tradition', 'innovation', 'preservation'])} is admirable, but rigidity will be your downfall. Learn to bend, or break.

To the keepers of {random.choice(world["artifacts"])}, I say: what you guard is both gift and curse. Use wisdom in choosing when to unlock and when to seal.

To every citizen of Aethermoor, I say: you matter more than you know. Your choices ripple outward in ways you cannot see. Choose with care. Choose with courage. Choose with hope.

THE PROPHECY'S FINAL WORDS

When three moons align and the old stars fade,
When ancient powers wake from slumber deep,
When faction stands with faction, blade to blade,
Then will the world either wake or sleep.

But know this truth that cuts through fear and night:
The future is not written in stone or star.
Every prophecy contains within its blight
The seeds of salvation from afar.

So walk with courage though the path be dark,
Stand with honor though the test be hard,
For in each heart there burns a vital spark
That neither shadow nor flame can discard.

Thus speaks {prophet} in Year {year}, having seen what may come. May those with wisdom hear and act. May those with courage face what must be faced. And may Aethermoor endure, transformed but not destroyed, tested but not broken.

The visions end. The voice falls silent. But the choice remains.

<|end_prophecy|>"""

    return text

def generate_long_treaty(world: Dict, target_words: int = 3500) -> str:
    """Generate extended treaty with detailed articles."""
    
    factions = random.sample(world["factions"], 3)
    year = random.randint(1230, 1260)
    location = random.choice(world["locations"])
    
    text = f"""<|treaty|>
Title: The Comprehensive Treaty of {location}
Date: Year {year}
Between: {factions[0]}, {factions[1]}, and {factions[2]}
Witnessed by: The Scholars of the Floating Library
Mediated by: {random.choice(world["characters"])}

PREAMBLE

WHEREAS the signatory factions have engaged in prolonged conflict causing suffering to their peoples and destabilization of the realm;

WHEREAS continued hostilities serve no constructive purpose and threaten catastrophic consequences;

WHEREAS all parties acknowledge the necessity of establishing lasting peace and frameworks for cooperation;

WHEREAS the discovery and handling of ancient artifacts requires coordinated response transcending faction boundaries;

WHEREAS future threats to Aethermoor demand unified defense strategies;

NOW THEREFORE, the undersigned representatives, having full authority to bind their respective factions, do hereby enter into this Comprehensive Treaty, effective immediately upon ratification.

ARTICLE I: CESSATION OF HOSTILITIES

Section 1.1: Immediate Ceasefire
All military operations between signatory factions shall cease immediately upon ratification of this treaty. "Military operations" is defined to include but not limited to: armed combat, sabotage, espionage operations targeting security interests, economic warfare, and proxy conflicts through allied groups.

Section 1.2: Withdrawal of Forces
Within ninety days of ratification, all military forces shall withdraw to positions held prior to the commencement of hostilities. Neutral observers from the Floating Library shall monitor and verify compliance.

Section 1.3: Prisoner Exchange
All prisoners of war shall be repatriated within sixty days. Both sides shall provide full accounting of all persons detained. Medical care and safe passage shall be guaranteed.

Section 1.4: Demilitarized Zones
The following territories are hereby designated as demilitarized zones: [detailed geographic descriptions follow]. No military installations, personnel, or equipment shall be positioned within these zones except as specifically permitted under Article VII (Joint Defense).

ARTICLE II: TERRITORIAL RECOGNITION

Section 2.1: Border Definitions
The borders between {factions[0]} and {factions[1]} are hereby established as follows: [detailed survey markers and geographic features]. These borders are recognized as permanent unless modified through peaceful negotiation.

Section 2.2: Disputed Territories
The territories of Shadow Nexus, The Neutral Grounds, and sections of The Wastes are recognized as contested. A joint commission shall be established to determine ultimate disposition through mediation rather than force.

Section 2.3: Free Movement Zones
Certain areas are designated as free movement zones where citizens of all factions may travel, trade, and reside subject to local laws: {random.choice(world["locations"])}, {random.choice(world["locations"])}, and designated trade corridors.

Section 2.4: Sacred and Historical Sites
Sites of cultural, historical, or spiritual significance shall be protected by joint agreement. No faction may unilaterally alter, exploit, or restrict access to these sites.

ARTICLE III: ECONOMIC COOPERATION

Section 3.1: Trade Agreements
Signatory factions agree to establish free trade zones and reduce tariffs on essential goods. Specifically: medical supplies, food staples, and educational materials shall be freely traded with minimal taxation.

Section 3.2: Resource Sharing
Scarce resources critical to multiple factions (specific minerals, magical reagents, ancient texts) shall be shared equitably through a distribution committee with equal representation.

Section 3.3: Infrastructure Development
Joint projects for roads, communication networks, and shared facilities shall be undertaken with costs and benefits distributed proportionally to population and usage.

Section 3.4: Currency and Banking
A common currency exchange system shall be established to facilitate inter-faction commerce. Banking regulations shall be harmonized to prevent exploitation.

ARTICLE IV: ARTIFACT AND KNOWLEDGE MANAGEMENT

Section 4.1: Discovery Protocol
Any faction discovering artifacts of significant power must notify all signatories within 72 hours. A joint assessment team shall be assembled to evaluate danger level and determine handling procedures.

Section 4.2: Research Cooperation
Research into ancient technology and magic shall be conducted through joint facilities with representatives from all factions. No faction shall pursue independent research into artifacts classified as "Category Omega" (world-threatening).

Section 4.3: Knowledge Sharing
All historical records, magical formulae, and technical specifications related to ancient civilizations shall be shared through the Floating Library, which maintains neutral custody and grants access to accredited researchers.

Section 4.4: Containment Procedures
Artifacts deemed too dangerous for active study shall be contained in jointly-guarded facilities. Seven separate locks, each controlled by different factions, shall prevent unilateral access.

ARTICLE V: DIPLOMATIC FRAMEWORK

Section 5.1: Permanent Embassies
Each faction shall establish and maintain embassies in the others' territories. These embassies shall enjoy diplomatic immunity and serve as channels for ongoing communication.

Section 5.2: Regular Summit Meetings
Leaders of all signatory factions shall convene quarterly at {location} to address ongoing issues, review treaty compliance, and coordinate responses to emerging challenges.

Section 5.3: Dispute Resolution Mechanism
Disputes arising under this treaty shall be resolved through mediation by neutral Scholars. If mediation fails, binding arbitration by a panel of three neutrals (one selected by each party) shall be employed.

Section 5.4: Cultural Exchange Programs
To build understanding and reduce prejudice, each faction shall host exchange scholars, artists, and students from the others. These programs shall receive protected funding.

ARTICLE VI: RIGHTS AND PROTECTIONS

Section 6.1: Civil Liberties
Citizens traveling or residing in another faction's territory shall enjoy basic rights including: freedom from arbitrary detention, right to legal representation, protection from discrimination, and right to practice cultural traditions not harmful to others.

Section 6.2: Refugee Protections
Persons fleeing persecution or disaster shall be granted temporary refuge regardless of faction of origin. Permanent resettlement shall be negotiated on case-by-case basis.

Section 6.3: Environmental Protections
All factions acknowledge responsibility for environmental stewardship. Industrial or magical activities causing cross-border environmental harm shall be jointly regulated.

Section 6.4: Historical Accountability
This treaty includes provision for truth and reconciliation commissions to address war crimes and atrocities. Focus shall be on justice and healing rather than vengeance.

ARTICLE VII: JOINT DEFENSE

Section 7.1: Mutual Defense Pact
An attack upon one signatory by external forces shall be considered an attack upon all. Coordinated military response shall be mandatory.

Section 7.2: Intelligence Sharing
Information regarding threats to collective security shall be shared immediately through secure channels. Joint intelligence committees shall coordinate analysis.

Section 7.3: Combined Forces Training
Joint military exercises shall be conducted annually to ensure interoperability. These exercises shall focus on defensive scenarios and disaster response.

Section 7.4: Emergency Response
In case of natural disaster, dimensional breach, or other catastrophic event, all factions pledge immediate mutual assistance regardless of political considerations.

ARTICLE VIII: AMENDMENT AND WITHDRAWAL

Section 8.1: Amendment Process
This treaty may be amended by unanimous consent of all signatories. Proposed amendments must be circulated for review at least 180 days before voting.

Section 8.2: Withdrawal Conditions
Any faction may withdraw from this treaty by providing 365 days written notice and demonstrating compliance with all existing obligations. Withdrawal does not nullify completed agreements.

Section 8.3: Violation and Enforcement
Material violations of this treaty shall be addressed first through diplomatic channels. If violations continue, economic sanctions may be imposed. Military enforcement is forbidden except in self-defense.

Section 8.4: Periodic Review
Every five years, a comprehensive review of this treaty shall be conducted to address changed circumstances and lessons learned from implementation.

ARTICLE IX: SPECIAL PROVISIONS

Section 9.1: Technology Transfer Limitations
While general cooperation is encouraged, each faction retains right to protect genuinely proprietary innovations. Balance between sharing and security shall be adjudicated by neutral panel.

Section 9.2: Magical Practice Regulation
Cross-faction magical practices must comply with safety standards established by joint committee. Certain dangerous magics are universally prohibited.

Section 9.3: Autonomous Groups
Smaller factions and independent groups not party to this treaty shall be encouraged to join or establish separate peace agreements. Signatory factions pledge not to exploit these groups against each other.

Section 9.4: Future Generations
Educational curricula in all factions shall include accurate history of the conflicts leading to this treaty, emphasizing lessons learned and importance of continued cooperation.

FINAL PROVISIONS

This treaty is executed in triplicate, with copies held by each signatory and the Floating Library. It shall be publicly posted and explained in common language so all citizens may understand rights and obligations it creates.

The signatory factions acknowledge that this treaty represents not an ending but a beginning - the start of a new era where cooperation replaces conflict, where dialogue supplants violence, where shared challenges receive united response.

We sign this document in full knowledge of the responsibility we bear to present and future generations. May it stand as testament to our commitment to peace and our faith that former enemies can become partners in building a better world.

SIGNED AND SEALED:

For {factions[0]}: [Signature and Seal]
Date: Year {year}, Day [  ]

For {factions[1]}: [Signature and Seal]  
Date: Year {year}, Day [  ]

For {factions[2]}: [Signature and Seal]
Date: Year {year}, Day [  ]

WITNESSED BY:
The Scholars of the Floating Library
[Signature and Seal of Head Chronicler]

<|end_treaty|>"""

    return text

def generate_8k_document(doc_type: str, world: Dict) -> Dict:
    """Generate a single 8K token document."""
    
    if doc_type == "chronicle":
        text = generate_long_chronicle(world, target_words=4000)
    elif doc_type == "prophecy":
        text = generate_long_prophecy(world, target_words=3000)
    elif doc_type == "treaty":
        text = generate_long_treaty(world, target_words=3500)
    else:
        # For other types, generate extended versions
        text = generate_long_chronicle(world, target_words=3500)
    
    word_count = len(text.split())
    
    return {
        "document_type": doc_type,
        "style": "long_form",
        "text": text,
        "metadata": {
            "word_count": word_count,
            "estimated_tokens": int(word_count * 1.3),  # Rough estimate
            "year": random.randint(1230, 1260),
            "quality_score": 0.95  # Long-form assumed high quality
        }
    }

def main():
    console.print(Panel.fit(
        "📚 [bold green]8K Token Document Generator[/bold green]\n\n"
        "Creating long-form narratives (4000-8000 tokens)\n"
        "For extended context training",
        border_style="green"
    ))
    
    # Configuration
    num_documents = console.input("\n[cyan]Number of documents to generate (default 1000):[/cyan] ") or "1000"
    num_documents = int(num_documents)
    
    console.print(f"\n[yellow]Generating {num_documents} long-form documents...[/yellow]\n")
    
    documents = []
    
    # Generate documents
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Generating...", total=num_documents)
        
        for i in range(num_documents):
            doc_type = random.choice(["chronicle", "prophecy", "treaty"])
            doc = generate_8k_document(doc_type, WORLD)
            documents.append(doc)
            progress.update(task, advance=1)
    
    # Save corpus
    timestamp = int(time.time())
    output_file = Path(f"experiments/8k_token_corpus_{timestamp}/training_data.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_words = sum(d["metadata"]["word_count"] for d in documents)
    total_tokens_est = sum(d["metadata"]["estimated_tokens"] for d in documents)
    avg_words = total_words / len(documents)
    
    console.print(f"\n[bold green]✅ Generation Complete![/bold green]\n")
    console.print(f"Total documents: {len(documents)}")
    console.print(f"Total words: {total_words:,}")
    console.print(f"Estimated tokens: {total_tokens_est:,}")
    console.print(f"Average words/doc: {avg_words:.0f}")
    console.print(f"Average tokens/doc: {total_tokens_est/len(documents):.0f}")
    console.print(f"\nSaved to: [bold]{output_file}[/bold]")
    
    # Size estimate
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    console.print(f"File size: {file_size_mb:.1f} MB")
    
    console.print(f"\n[bold yellow]Training Estimates:[/bold yellow]")
    console.print(f"• Training time (A10): ~{len(documents) * 0.05:.0f} hours")
    console.print(f"• Training cost (A10 @ $0.75/hr): ~${len(documents) * 0.05 * 0.75:.2f}")

if __name__ == "__main__":
    main()
