import click
import json
import sys
import os
from typing import Optional

from src.database import Database
from src.assessment import AssessmentEngine
from src.deduplication import DeduplicationEngine
from src.synthesis import SynthesisEngine

DEFAULT_DB_PATH = "data/foresight_studio.db"

def get_db(db_path: str) -> Database:
    return Database(db_path)

@click.group()
def cli():
    """Foresight Studio Pipeline CLI Engine"""
    pass

@cli.command()
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database file.')
def init_db(db_path):
    """Initialize the SQLite Knowledge Graph schema."""
    try:
        db = get_db(db_path)
        db.close()
        click.echo(f"Database successfully initialized at: {db_path}")
    except Exception as e:
        click.echo(f"Failed to initialize database: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('json_path')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database file.')
def ingest(json_path, db_path):
    """Ingest raw signals from a JSON file and run Multi-Model Assessment."""
    if not os.path.exists(json_path):
        click.echo(f"Error: JSON file not found at: {json_path}", err=True)
        sys.exit(1)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_signals = json.load(f)
    except Exception as e:
        click.echo(f"Error parsing JSON: {e}", err=True)
        sys.exit(1)

    if not isinstance(raw_signals, list):
        click.echo("Error: JSON must contain a root-level list of signal objects.", err=True)
        sys.exit(1)

    db = get_db(db_path)
    assessment = AssessmentEngine()

    click.echo(f"Starting ingestion of {len(raw_signals)} signal(s)...")
    ingested_count = 0
    
    for idx, raw_sig in enumerate(raw_signals):
        try:
            # Validate required fields
            if "title" not in raw_sig or "description" not in raw_sig or "category" not in raw_sig:
                click.echo(f"Skipping signal index {idx}: Missing required field 'title', 'description', or 'category'.")
                continue

            # Run Stage 1 Assessment (LLM or Heuristic)
            click.echo(f" Assessing: \"{raw_sig['title']}\"")
            assessment_results = assessment.assess_signal(
                title=raw_sig["title"],
                description=raw_sig["description"],
                category=raw_sig["category"]
            )

            # Blend raw fields and assessment results
            signal_record = {
                "id": raw_sig.get("id"),
                "title": raw_sig["title"],
                "description": raw_sig["description"],
                "category": raw_sig["category"],
                "source_url": raw_sig.get("source_url"),
                "source_type": raw_sig.get("source_type"),
                "date_observed": raw_sig.get("date_observed"),
                "geography": raw_sig.get("geography"),
                "sector": raw_sig.get("sector"),
                "tags": raw_sig.get("tags", []),
                "confidence_score": raw_sig.get("confidence_score", 5),
                "novelty_score": raw_sig.get("novelty_score", 5),
                
                # Merged metrics
                "impact_score": assessment_results["impact_score"],
                "time_horizon": assessment_results["time_horizon"],
                "strategic_relevance": assessment_results["strategic_relevance"],
                "actionability": assessment_results["actionability"],
                "uncertainty_score": assessment_results["uncertainty_score"],
                "horizon_year": assessment_results["horizon_year"],
                "polarity": raw_sig.get("polarity", "Emergent"),
                "shadow_type": raw_sig.get("shadow_type"),
                "mitigation_notes": raw_sig.get("mitigation_notes"),

                # Defaults for deduplication
                "status": "Shadow", # Starts as a weak "Shadow" research point
                "is_keeper": 1,
                "keeper_id": None,
                "convergence_score": 1.0,
                "source_metadata": []
            }

            sig_id = db.add_signal(signal_record)
            click.echo(f" Saved ID: {sig_id}")
            ingested_count += 1

        except Exception as e:
            click.echo(f"Failed to ingest signal index {idx}: {e}", err=True)

    db.close()
    click.echo(f"Ingestion complete. Successfully processed and saved {ingested_count} signals.")

@cli.command()
@click.option('--threshold', default=0.75, help='Similarity threshold coefficient (0.50 - 0.95).')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def deduplicate(threshold, db_path):
    """Run Stage 2 Semantic Deduplication and Medoid clustering."""
    db = get_db(db_path)
    engine = DeduplicationEngine(threshold=threshold)
    
    click.echo(f"Executing semantic clustering (similarity threshold: {threshold})...")
    try:
        keepers, dups = engine.deduplicate_database(db)
        click.echo(f"Deduplication finished.")
        click.echo(f" -> Active Keepers isolated (verified Signals): {keepers}")
        click.echo(f" -> Redundant duplicates nested (Shadow research): {dups}")
    except Exception as e:
        click.echo(f"Deduplication process failed: {e}", err=True)
        db.close()
        sys.exit(1)
        
    db.close()

@cli.command()
@click.option('--format', default='json', type=click.Choice(['json', 'table']), help='Output format format.')
@click.option('--output', default=None, help='File path to export radar node parameters.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def radar(format, output, db_path):
    """Export the visual polar radar coordinates and parameters of active keepers."""
    db = get_db(db_path)
    engine = SynthesisEngine()
    
    try:
        nodes = engine.generate_radar_json(db)
    except Exception as e:
        click.echo(f"Failed to compile radar layout: {e}", err=True)
        db.close()
        sys.exit(1)
        
    db.close()

    if format == 'json':
        output_str = json.dumps(nodes, indent=2)
    else:
        # Table format
        lines = [f"{'ID':<12} | {'Category':<15} | {'Horizon':<10} | {'Impact':<6} | {'Theta':<6} | {'Radius':<6} | {'Title'}"]
        lines.append("-" * 90)
        for n in nodes:
            lines.append(f"{n['id']:<12} | {n['category']:<15} | {n['time_horizon']:<10} | {n['impact_score']:<6} | {n['theta_degrees']:<6.1f} | {n['radius']:<6.1f} | {n['title']}")
        output_str = "\n".join(lines)

    if output:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True) if os.path.dirname(output) else None
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            click.echo(f"Successfully exported polar radar data to: {output}")
        except Exception as e:
            click.echo(f"Failed to write export: {e}", err=True)
    else:
        click.echo(output_str)

@cli.command()
@click.option('--output', default='synthesis_report.md', help='Output filepath for synthesized report.')
@click.option('--db-path', default=DEFAULT_DB_PATH, help='Path to SQLite database.')
def report(output, db_path):
    """Compile a master Strategic Foresight Report compiling high-impact issues."""
    db = get_db(db_path)
    engine = SynthesisEngine()
    
    click.echo("Generating Foresight Synthesis Narrative...")
    try:
        report_md = engine.compile_markdown_report(db)
    except Exception as e:
        click.echo(f"Report generation failed: {e}", err=True)
        db.close()
        sys.exit(1)
        
    db.close()

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True) if os.path.dirname(output) else None
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report_md)
        click.echo(f"Strategic report successfully written to: {output}")
    except Exception as e:
        click.echo(f"Failed to write report file: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
