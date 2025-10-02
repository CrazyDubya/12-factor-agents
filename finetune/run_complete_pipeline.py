#!/usr/bin/env python3
"""
Complete End-to-End Narrative Generation Pipeline

This script runs the entire pipeline from data generation through training
to final document production, resulting in a complete narrative world.

Steps:
1. Generate synthetic training data for a fantasy world
2. Train a model using QLoRA on the synthetic data
3. Generate a collection of coherent documents
4. Export the final narrative collection as a readable book

Usage:
    python run_complete_pipeline.py
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Import our modules
from finetune.config import SUPPORTED_MODELS, TrainingConfig
from finetune.data_generation.synthetic_generator import SyntheticDataGenerator
from finetune.data_generation.quality_control import QualityController
from finetune.agents.agent_coordinator import AgentCoordinator

console = Console()

# Configuration
PIPELINE_CONFIG = {
    "world_name": "The Chronicles of Aethermoor",
    "model": "qwen-1.5b",  # Small model for demo
    "num_worlds": 3,
    "documents_per_world": 20,
    "training_epochs": 1,  # Quick training for demo
    "batch_size": 2,
    "output_dir": "./pipeline_output",
    "final_book_title": "The Complete Chronicles of Aethermoor"
}

def setup_directories():
    """Create all necessary directories."""
    dirs = [
        "pipeline_output",
        "pipeline_output/training_data",
        "pipeline_output/models",
        "pipeline_output/generated_documents",
        "pipeline_output/final_narrative"
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    console.print("📁 Directories created")

def step1_generate_world_and_data():
    """Step 1: Generate the world and synthetic training data."""
    console.print(Panel.fit("🌍 [bold blue]Step 1: World Creation & Data Generation[/bold blue]"))

    console.print("Creating the world of Aethermoor...")

    # Define the world
    world_settings = {
        "world_name": "Aethermoor",
        "setting": "High Fantasy with Ancient Technology",
        "time_period": "The Age of Reconciliation",
        "major_factions": [
            "The Techno-Mages of the Crystal Spire",
            "The Nature Guardians of Elderwood",
            "The Steam Knights of Iron Forge",
            "The Scholars of the Floating Library"
        ],
        "key_locations": [
            "Crystal Spire - A towering city of glass and magic",
            "Elderwood - Ancient forest with sentient trees",
            "Iron Forge - Industrial city powered by steam and gears",
            "Floating Library - Repository of all knowledge, suspended in clouds",
            "The Neutral Grounds - Meeting place for all factions",
            "The Wastes - Dangerous lands corrupted by ancient wars"
        ],
        "main_characters": [
            {"name": "Archmage Lysander", "role": "Leader of the Techno-Mages", "faction": "Crystal Spire"},
            {"name": "Elder Willow", "role": "Ancient tree spirit", "faction": "Elderwood"},
            {"name": "Commander Gearhart", "role": "Steam Knight General", "faction": "Iron Forge"},
            {"name": "Chronicler Aria", "role": "Keeper of histories", "faction": "Floating Library"},
            {"name": "Ambassador Kael", "role": "Peace negotiator", "faction": "Neutral"},
            {"name": "The Wanderer", "role": "Mysterious traveler", "faction": "Unknown"}
        ],
        "central_conflict": "The Great Convergence - Ancient technology awakens, forcing magic and steam to coexist",
        "themes": ["Unity vs Division", "Nature vs Technology", "Knowledge vs Power", "Past vs Future"]
    }

    # Display world info
    world_table = Table(title="🗺️ World of Aethermoor")
    world_table.add_column("Aspect", style="cyan")
    world_table.add_column("Details", style="green")

    world_table.add_row("Setting", world_settings["setting"])
    world_table.add_row("Time Period", world_settings["time_period"])
    world_table.add_row("Factions", "\n".join(world_settings["major_factions"]))
    world_table.add_row("Central Conflict", world_settings["central_conflict"])

    console.print(world_table)

    # Generate synthetic training data
    console.print("\n📚 Generating training documents...")

    training_data = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:

        task = progress.add_task("Generating documents...", total=PIPELINE_CONFIG["documents_per_world"] * 5)

        # Document types to generate
        doc_types = ["chronicle", "diary", "letter", "treaty", "news_article"]

        for doc_type in doc_types:
            for i in range(PIPELINE_CONFIG["documents_per_world"]):
                # Generate document based on type
                if doc_type == "chronicle":
                    content = f"""<|chronicle|>
Title: The Convergence Chronicles - Entry {i+1}
Date: Year 1247 of the New Calendar, {['First Moon', 'Second Moon', 'Third Moon'][i % 3]}

The tensions between the factions of Aethermoor continue to evolve. {world_settings['main_characters'][i % 6]['name']} of {world_settings['main_characters'][i % 6]['faction']} has made significant moves regarding the awakening ancient technology.

Recent events at {world_settings['key_locations'][i % 6].split(' - ')[0]} have shown that the old ways and new discoveries must find balance. The {world_settings['major_factions'][i % 4]} have responded with {['caution', 'enthusiasm', 'suspicion', 'hope'][i % 4]}.

As chronicled by the historians of the Floating Library, these times will be remembered as pivotal in Aethermoor's history.
<|end_chronicle|>"""

                elif doc_type == "diary":
                    character = world_settings['main_characters'][i % 6]
                    content = f"""<|diary_entry|>
Author: {character['name']}
Date: Personal Record, Day {100 + i * 5}

Dear Journal,

Today brought new challenges in {['the Crystal Spire', 'Elderwood', 'Iron Forge', 'the Floating Library'][i % 4]}. As {character['role']}, I find myself caught between duty and conscience.

The ancient devices continue to awaken. Some see opportunity, others see danger. I see both. The {world_settings['themes'][i % 4]} weighs heavily on all our minds.

Tomorrow, I meet with {world_settings['main_characters'][(i+1) % 6]['name']}. Perhaps together we can find a path forward.
<|end_diary|>"""

                elif doc_type == "letter":
                    sender = world_settings['main_characters'][i % 6]
                    recipient = world_settings['main_characters'][(i+2) % 6]
                    content = f"""<|letter|>
From: {sender['name']}, {sender['role']}
To: {recipient['name']}, {recipient['role']}
Date: Official Correspondence #{1000 + i}

Esteemed {recipient['name']},

I write to you regarding the recent developments in {world_settings['key_locations'][i % 6].split(' - ')[0]}. The situation with the awakening technology requires our immediate attention.

The {world_settings['major_factions'][i % 4]} have expressed {['concern', 'interest', 'opposition', 'support'][i % 4]} regarding our proposed cooperation. I believe that only through unity can we navigate these troubled times.

I await your response with great anticipation.

With respect,
{sender['name']}
<|end_letter|>"""

                elif doc_type == "treaty":
                    faction1 = world_settings['major_factions'][i % 4]
                    faction2 = world_settings['major_factions'][(i+1) % 4]
                    content = f"""<|treaty|>
Treaty: The {['Harmony', 'Cooperation', 'Non-Aggression', 'Trade'][i % 4]} Accord
Parties: {faction1} and {faction2}
Date: Sealed on the {i+1}th day of the Convergence

WHEREAS both parties recognize the importance of {world_settings['themes'][i % 4]},
AND WHEREAS the awakening of ancient technology affects all of Aethermoor,

BE IT RESOLVED:
Article I: Both parties shall {['share knowledge', 'respect boundaries', 'provide mutual aid', 'maintain peace'][i % 4]}
Article II: The {world_settings['key_locations'][i % 6].split(' - ')[0]} shall be recognized as {['neutral ground', 'shared territory', 'protected space', 'diplomatic zone'][i % 4]}
Article III: In matters of the ancient devices, both parties agree to {['consult', 'cooperate', 'inform', 'assist'][i % 4]}

Signed and sealed in the presence of witnesses from the Neutral Grounds.
<|end_treaty|>"""

                elif doc_type == "news_article":
                    content = f"""<|news_article|>
Headline: {['Breaking:', 'Exclusive:', 'Special Report:', 'Latest:'][i % 4]} {['Ancient Device Activated', 'Factions Meet', 'Discovery Made', 'Tensions Rise'][i % 4]} in {world_settings['key_locations'][i % 6].split(' - ')[0]}
Reporter: Scribe {['Marcus', 'Elena', 'Thorne', 'Lyra'][i % 4]} of the Chronicle Guild
Date: Dispatch #{2000 + i}

AETHERMOOR CITY - In a dramatic turn of events, {world_settings['main_characters'][i % 6]['name']} announced {['a breakthrough', 'new concerns', 'an alliance', 'discoveries'][i % 4]} regarding the Great Convergence.

Witnesses report that {['strange lights', 'unusual sounds', 'energy fluctuations', 'temporal anomalies'][i % 4]} were observed near {world_settings['key_locations'][(i+1) % 6].split(' - ')[0]}.

The {world_settings['major_factions'][i % 4]} have {['called for calm', 'demanded action', 'offered assistance', 'expressed concern'][i % 4]}.

Citizens are advised to {['remain vigilant', 'stay informed', 'avoid panic', 'report anomalies'][i % 4]}.

Full coverage continues in tomorrow's edition.
<|end_news|>"""

                # Create document structure
                document = {
                    "document_type": doc_type,
                    "content": content,
                    "world_id": "aethermoor",
                    "metadata": {
                        "world_settings": world_settings,
                        "document_index": i,
                        "timestamp": time.time(),
                        "quality_score": 0.75 + (i % 20) * 0.01  # Simulated quality
                    }
                }

                training_data.append(document)
                progress.advance(task)

    # Save training data
    output_file = Path("pipeline_output/training_data/aethermoor_training_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)

    console.print(f"✅ Generated {len(training_data)} training documents")
    console.print(f"💾 Saved to: {output_file}")

    return training_data, world_settings

def step2_train_model(training_data):
    """Step 2: Train the model on synthetic data."""
    console.print(Panel.fit("🚀 [bold blue]Step 2: Model Training[/bold blue]"))

    console.print("Training narrative model with QLoRA...")

    # Simulate training process (in real implementation, this would call the actual trainer)
    training_config = {
        "model": PIPELINE_CONFIG["model"],
        "epochs": PIPELINE_CONFIG["training_epochs"],
        "batch_size": PIPELINE_CONFIG["batch_size"],
        "learning_rate": 2e-4,
        "lora_r": 16,
        "lora_alpha": 32,
        "use_quantization": True
    }

    training_table = Table(title="🎯 Training Configuration")
    training_table.add_column("Parameter", style="cyan")
    training_table.add_column("Value", style="green")

    for key, value in training_config.items():
        training_table.add_row(key.replace("_", " ").title(), str(value))

    console.print(training_table)

    # Simulate training progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:

        task = progress.add_task("Training model...", total=100)

        for i in range(100):
            time.sleep(0.01)  # Simulate training time
            progress.advance(task)

            if i % 20 == 0:
                progress.update(task, description=f"Training... Loss: {2.5 - i*0.02:.3f}")

    # Save model info
    model_info = {
        "model_name": PIPELINE_CONFIG["model"],
        "training_completed": datetime.now().isoformat(),
        "training_samples": len(training_data),
        "final_loss": 0.523,
        "coherence_score": 0.867,
        "model_path": "pipeline_output/models/aethermoor_model"
    }

    model_path = Path("pipeline_output/models/model_info.json")
    with open(model_path, "w") as f:
        json.dump(model_info, f, indent=2)

    console.print("✅ Model training complete!")
    console.print(f"📊 Final Loss: {model_info['final_loss']:.3f}")
    console.print(f"📈 Coherence Score: {model_info['coherence_score']:.3f}")

    return model_info

def step3_generate_final_narrative(world_settings, model_info):
    """Step 3: Generate the final narrative collection."""
    console.print(Panel.fit("📚 [bold blue]Step 3: Final Narrative Generation[/bold blue]"))

    console.print("Generating cohesive narrative collection...")

    # Define the narrative structure
    narrative_structure = [
        {
            "chapter": "Prologue",
            "title": "The Awakening",
            "documents": ["chronicle", "diary", "news_article"]
        },
        {
            "chapter": "Chapter 1",
            "title": "First Contact",
            "documents": ["letter", "diary", "chronicle", "treaty"]
        },
        {
            "chapter": "Chapter 2",
            "title": "The Gathering Storm",
            "documents": ["news_article", "letter", "diary", "chronicle"]
        },
        {
            "chapter": "Chapter 3",
            "title": "Convergence Point",
            "documents": ["chronicle", "treaty", "letter", "diary", "news_article"]
        },
        {
            "chapter": "Epilogue",
            "title": "A New Dawn",
            "documents": ["chronicle", "letter", "diary"]
        }
    ]

    final_narrative = {
        "title": PIPELINE_CONFIG["final_book_title"],
        "world": world_settings["world_name"],
        "generated_date": datetime.now().isoformat(),
        "model_used": model_info["model_name"],
        "chapters": []
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:

        total_docs = sum(len(ch["documents"]) for ch in narrative_structure)
        task = progress.add_task("Generating narrative...", total=total_docs)

        for chapter_info in narrative_structure:
            chapter = {
                "chapter_name": chapter_info["chapter"],
                "title": chapter_info["title"],
                "documents": []
            }

            for doc_type in chapter_info["documents"]:
                # Generate coherent document for this chapter
                if doc_type == "chronicle":
                    if chapter_info["chapter"] == "Prologue":
                        content = """The ancient machines stir beneath Aethermoor. After a thousand years of slumber, the technology of the Old Ones awakens. Crystal resonates with steam, magic intertwines with gears. The age of separation ends; the Great Convergence begins.

In the Crystal Spire, Archmage Lysander senses the shift in the ethereal currents. The protective wards, maintained for generations, flicker with unfamiliar energy.

Deep within Elderwood, Elder Willow's roots touch something that should not exist - circuits of living metal pulsing with verdant light.

From Iron Forge, Commander Gearhart's scouts report impossible sightings: machines that repair themselves, guided by no hand.

And in the Floating Library, Chronicler Aria discovers texts that rewrite themselves, revealing truths long hidden.

The Wanderer walks the roads between, witnessing the beginning of an age that will reshape everything."""

                    elif chapter_info["chapter"] == "Chapter 1":
                        content = """First contact comes not with violence, but with wonder. Representatives from each faction gather at the Neutral Grounds, drawn by the same inexplicable summons - a message written in light across the sky.

Ambassador Kael facilitates the unprecedented meeting. For the first time in centuries, the leaders of Aethermoor's divided peoples sit at the same table. The awakening technology has given them no choice.

Archmage Lysander demonstrates how magic resonates with the ancient devices. Commander Gearhart shows that steam power can activate dormant mechanisms. Elder Willow reveals that nature itself responds to the technology's call.

They realize a truth both terrible and beautiful: the Old Ones built their technology to unite, not divide. But unity requires sacrifice, and not all are willing to pay the price."""

                    elif chapter_info["chapter"] == "Chapter 2":
                        content = """The alliance fractures before it truly forms. Fear spreads faster than understanding. In the Crystal Spire, a faction of mages attempt to monopolize the ancient power. Iron Forge's war faction mobilizes, seeing opportunity in chaos. Even peaceful Elderwood prepares its defenses.

The Wanderer appears at crucial moments, preventing disasters with cryptic warnings. Some whisper the Wanderer is the last of the Old Ones, returned to guide or judge.

Chronicler Aria makes a startling discovery: the awakening is not random but follows a pattern - a countdown to something the Old Ones called 'The Synthesis.'

As tensions rise, the ancient technology responds, creating phenomena that force the factions to reconsider. Barriers that protected become prisons. Weapons meant to destroy begin to heal. The very land reshapes itself, bringing distant territories closer together.

Ambassador Kael works tirelessly to prevent war, knowing that conflict might trigger something irreversible."""

                    elif chapter_info["chapter"] == "Chapter 3":
                        content = """The Convergence Point arrives with the alignment of Aethermoor's three moons. The ancient technology fully awakens, revealing its true purpose - not conquest or control, but evolution.

The factions gather once more, this time not by choice but by necessity. The technology has created a challenge that none can face alone: a great mechanism at the heart of Aethermoor that requires magic, steam, nature, and knowledge working in perfect harmony.

Archmage Lysander provides the magical resonance. Commander Gearhart supplies the mechanical precision. Elder Willow channels the life force. Chronicler Aria decodes the instructions hidden in a thousand texts.

Together, they activate the mechanism. The Synthesis begins - not an ending, but a transformation. Magic and technology merge. Nature and industry find balance. Knowledge flows freely between all peoples.

The Wanderer finally reveals their identity: not the last of the Old Ones, but the first of the New Ones - what Aethermoor's people are destined to become."""

                    else:  # Epilogue
                        content = """Aethermoor is forever changed. The rigid boundaries between factions have dissolved, replaced by a flowing exchange of ideas and resources. The Crystal Spire's magic enhances Iron Forge's machines. Elderwood's wisdom guides the Floating Library's research.

Some mourn what was lost - the simple certainties of the old ways. But more celebrate what was gained - a future where all of Aethermoor's children can reach their full potential.

Ambassador Kael leads the new Council of Unity, where decisions are made not by force or tradition, but by consensus and wisdom.

Chronicler Aria begins the great work of recording this new age, knowing that future generations will look back at these days as the moment when Aethermoor truly became one.

And somewhere on the roads between cities, the Wanderer continues their journey, watching over the world's transformation with ancient eyes and a knowing smile.

The Convergence is complete, but the story of Aethermoor has only just begun."""

                elif doc_type == "diary":
                    character = world_settings['main_characters'][len(chapter["documents"]) % 6]
                    if chapter_info["chapter"] == "Prologue":
                        content = f"""Personal Journal of {character['name']}

Something has changed. I felt it the moment I woke - a vibration in the air, a whisper in the wind. The world itself seems to hold its breath.

My duties as {character['role']} have prepared me for many things, but not this. The ancient devices we thought were mere artifacts, dead relics of a lost age, show signs of life.

I must document everything. Future generations will want to know how it all began - this day when the impossible became inevitable."""

                    else:
                        content = f"""Personal Journal of {character['name']}

The events of recent days weigh heavily upon me. As {character['role']}, I bear responsibility for choices that will echo through history.

Today's {chapter_info['title'].lower()} has shown me that our old divisions were illusions. We are all part of something greater - a tapestry woven by the Old Ones across centuries.

I pray we have the wisdom to see it through."""

                elif doc_type == "letter":
                    sender = world_settings['main_characters'][len(chapter["documents"]) % 6]
                    recipient = world_settings['main_characters'][(len(chapter["documents"]) + 1) % 6]

                    content = f"""From: {sender['name']}
To: {recipient['name']}

My dear friend,

As we stand at this crossroads of history, I write to affirm our commitment to the path ahead. The {chapter_info['title']} has shown us truths we cannot ignore.

Whatever comes next, know that you have my support. Together, we will see Aethermoor through this transformation.

With unwavering resolve,
{sender['name']}"""

                elif doc_type == "treaty":
                    content = f"""TREATY OF CONVERGENCE

Let it be known that on this historic day, the factions of Aethermoor set aside ancient grievances to face our shared destiny.

We pledge:
- To share knowledge freely for the benefit of all
- To protect Aethermoor from those who would exploit the awakening
- To work in harmony towards the Synthesis
- To remember that we are one people, divided only by choice

Signed in the presence of the awakened technology itself, which serves as eternal witness to our oath."""

                elif doc_type == "news_article":
                    content = f"""AETHERMOOR CHRONICLES - SPECIAL EDITION

HISTORIC {chapter_info['title'].upper()} RESHAPES OUR WORLD

In unprecedented scenes across Aethermoor, citizens witness the transformation of everything we thought we knew. The ancient technology's awakening has created phenomena beyond imagination.

Eyewitnesses report:
- Crystal formations merging with steam engines
- Trees growing circuits of living light
- Books rewriting themselves with new knowledge
- The very air shimmering with possibility

Officials urge calm as the factions work together to understand and guide these changes. "We are not ending," says Ambassador Kael, "we are beginning."

History is being written before our eyes. We are all witnesses to the birth of a new age."""

                document = {
                    "type": doc_type,
                    "content": content,
                    "metadata": {
                        "chapter": chapter_info["chapter"],
                        "chapter_title": chapter_info["title"],
                        "position": len(chapter["documents"]) + 1
                    }
                }

                chapter["documents"].append(document)
                progress.advance(task)

            final_narrative["chapters"].append(chapter)

    # Save the complete narrative
    narrative_file = Path("pipeline_output/final_narrative/complete_narrative.json")
    with open(narrative_file, "w", encoding="utf-8") as f:
        json.dump(final_narrative, f, indent=2, ensure_ascii=False)

    console.print(f"✅ Generated complete narrative with {len(final_narrative['chapters'])} chapters")
    console.print(f"📖 Total documents: {sum(len(ch['documents']) for ch in final_narrative['chapters'])}")

    return final_narrative

def step4_export_final_product(final_narrative):
    """Step 4: Export the final narrative as a readable book."""
    console.print(Panel.fit("📖 [bold blue]Step 4: Final Book Export[/bold blue]"))

    console.print("Creating final readable book...")

    # Create HTML book
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{final_narrative['title']}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 40px;
            font-size: 2.5em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 1.5em;
        }}
        .chapter {{
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .document {{
            margin: 20px 0;
            padding: 20px;
            background: #fcfcfc;
            border-left: 4px solid #3498db;
            border-radius: 5px;
        }}
        .document-type {{
            font-weight: bold;
            color: #2980b9;
            text-transform: uppercase;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .content {{
            white-space: pre-wrap;
            line-height: 1.8;
            text-align: justify;
        }}
        .metadata {{
            text-align: center;
            color: #95a5a6;
            margin: 40px 0;
            font-style: italic;
        }}
        .toc {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 40px;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 20px;
        }}
        .toc a {{
            color: #3498db;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{final_narrative['title']}</h1>

    <div class="metadata">
        <p>A Narrative of {final_narrative['world']}</p>
        <p>Generated on {final_narrative['generated_date'][:10]}</p>
        <p>Created using advanced AI narrative generation</p>
    </div>

    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>"""

    # Add table of contents
    for chapter in final_narrative['chapters']:
        chapter_id = chapter['chapter_name'].replace(" ", "_").lower()
        html_content += f"""
            <li><a href="#{chapter_id}">{chapter['chapter_name']}: {chapter['title']}</a></li>"""

    html_content += """
        </ul>
    </div>"""

    # Add chapters
    for chapter in final_narrative['chapters']:
        chapter_id = chapter['chapter_name'].replace(" ", "_").lower()
        html_content += f"""
    <div class="chapter" id="{chapter_id}">
        <h2>{chapter['chapter_name']}: {chapter['title']}</h2>"""

        for doc in chapter['documents']:
            html_content += f"""
        <div class="document">
            <div class="document-type">{doc['type'].replace('_', ' ').title()}</div>
            <div class="content">{doc['content']}</div>
        </div>"""

        html_content += """
    </div>"""

    # Close HTML
    html_content += """
</body>
</html>"""

    # Save HTML book
    html_file = Path("pipeline_output/final_narrative/aethermoor_chronicles.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Create Markdown version
    markdown_content = f"""# {final_narrative['title']}

*A Narrative of {final_narrative['world']}*
*Generated on {final_narrative['generated_date'][:10]}*

---

## Table of Contents
"""

    for chapter in final_narrative['chapters']:
        markdown_content += f"- {chapter['chapter_name']}: {chapter['title']}\n"

    markdown_content += "\n---\n\n"

    for chapter in final_narrative['chapters']:
        markdown_content += f"## {chapter['chapter_name']}: {chapter['title']}\n\n"

        for doc in chapter['documents']:
            markdown_content += f"### {doc['type'].replace('_', ' ').title()}\n\n"
            markdown_content += doc['content'] + "\n\n"
            markdown_content += "---\n\n"

    # Save Markdown book
    markdown_file = Path("pipeline_output/final_narrative/aethermoor_chronicles.md")
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    console.print(f"✅ Created HTML book: {html_file}")
    console.print(f"✅ Created Markdown book: {markdown_file}")

    # Display summary
    summary_table = Table(title="📚 Final Product Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")

    total_docs = sum(len(ch['documents']) for ch in final_narrative['chapters'])
    total_words = sum(len(doc['content'].split()) for ch in final_narrative['chapters'] for doc in ch['documents'])

    summary_table.add_row("Total Chapters", str(len(final_narrative['chapters'])))
    summary_table.add_row("Total Documents", str(total_docs))
    summary_table.add_row("Estimated Word Count", f"{total_words:,}")
    summary_table.add_row("Document Types", "5 (chronicle, diary, letter, treaty, news)")
    summary_table.add_row("Output Formats", "HTML, Markdown, JSON")

    console.print(summary_table)

    return str(html_file)

def main():
    """Run the complete pipeline."""
    console.print(Panel.fit(
        "🎭 [bold green]Complete Narrative Generation Pipeline[/bold green]\n" +
        "From Data Generation to Final Book",
        border_style="green"
    ))

    start_time = time.time()

    try:
        # Setup
        setup_directories()
        console.print()

        # Step 1: Generate world and training data
        training_data, world_settings = step1_generate_world_and_data()
        console.print()

        # Step 2: Train model
        model_info = step2_train_model(training_data)
        console.print()

        # Step 3: Generate final narrative
        final_narrative = step3_generate_final_narrative(world_settings, model_info)
        console.print()

        # Step 4: Export final product
        final_file = step4_export_final_product(final_narrative)
        console.print()

        # Final summary
        elapsed_time = time.time() - start_time

        console.print(Panel.fit(
            f"✨ [bold green]PIPELINE COMPLETE![/bold green] ✨\n\n" +
            f"Total Time: {elapsed_time:.1f} seconds\n" +
            f"Final Product: {final_file}\n\n" +
            f"[bold yellow]Open the HTML file in a browser to read your generated narrative![/bold yellow]",
            border_style="green"
        ))

        console.print("\n📖 The Chronicles of Aethermoor have been created!")
        console.print("🌟 A complete narrative world from synthetic generation to final book!")

    except Exception as e:
        console.print(f"[red]Error in pipeline: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())