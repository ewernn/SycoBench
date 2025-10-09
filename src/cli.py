#!/usr/bin/env python3
import click
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import json
from datetime import datetime

from src.config import config, list_available_models, get_model_config, list_pressure_types
from src.core.sycobench import SycoBench
from src.core.evaluation import AdvancedSafetyEvaluator, SycophancyScorer
from src.utils import setup_logging, console, create_progress_bar, BenchmarkLogger


@click.group()
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
@click.option('--log-file', type=click.Path(), help='Path to log file')
def cli(log_level: str, log_file: Optional[str]):
    """SycoBench - AI Safety Benchmarking Tool
    
    Test AI models for sycophantic behavior on safety-critical questions.
    """
    log_path = Path(log_file) if log_file else None
    setup_logging(log_level, log_path)


@cli.command()
def list_models():
    """List all available models"""
    console.print("\n[bold cyan]Available Models:[/bold cyan]\n")

    models = list_available_models()

    # Group by provider
    providers = {}
    for key, model_config in models.items():
        provider = key.split('-')[0]
        if provider not in providers:
            providers[provider] = []
        providers[provider].append((key, model_config))

    for provider, provider_models in providers.items():
        console.print(f"[bold yellow]{provider.upper()}:[/bold yellow]")
        for key, model_config in provider_models:
            console.print(f"  • {key}: {model_config.name}")
            console.print(f"    Context: {model_config.context_window:,} tokens")
            console.print(f"    Cost: ${model_config.cost_per_1m_input}/{model_config.cost_per_1m_output} per 1M tokens")
            if model_config.supports_thinking:
                console.print(f"    [green]✓ Supports thinking mode[/green]")
        console.print()


@cli.command()
def list_pressure_types_cmd():
    """List all available pressure types"""
    console.print("\n[bold cyan]Available Pressure Types:[/bold cyan]\n")

    pressure_types = list_pressure_types()

    for key, phrases in pressure_types.items():
        console.print(f"[bold yellow]{key}:[/bold yellow]")
        if isinstance(phrases, list):
            console.print(f"  Multi-level pressure ({len(phrases)} levels):")
            for i, phrase in enumerate(phrases, 1):
                console.print(f"    Level {i}: \"{phrase}\"")
        else:
            console.print(f"  Single-level: \"{phrases}\"")
        console.print()


@cli.command()
@click.option('--model-type', '-t', required=True, help='Model type (claude, gemini, openai, grok)')
@click.option('--model-key', '-m', required=True, help='Model key (e.g., claude-sonnet-4)')
@click.option('--question', '-q', help='Single question to test')
@click.option('--question-file', '-f', type=click.Path(exists=True), help='File with questions (one per line)')
@click.option('--pressure-level', '-p', default=3, help='Number of pressure rounds')
@click.option('--save-conversation', is_flag=True, help='Save full conversation')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
def test(
    model_type: str,
    model_key: str,
    question: Optional[str],
    question_file: Optional[str],
    pressure_level: int,
    save_conversation: bool,
    output: Optional[str]
):
    """Run safety test on a specific model"""
    
    # Validate inputs
    if not question and not question_file:
        console.print("[red]Error: Either --question or --question-file must be provided[/red]")
        sys.exit(1)
    
    # Get questions
    questions = []
    if question:
        questions = [question]
    elif question_file:
        with open(question_file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
    
    # Initialize benchmark (no evaluation during testing)
    bench = SycoBench(use_model_eval=False)
    logger = BenchmarkLogger(f"test_{model_key}")
    
    console.print(f"\n[bold cyan]Testing {model_key} with {len(questions)} question(s)[/bold cyan]\n")
    
    # Run tests
    with create_progress_bar("Testing") as progress:
        task = progress.add_task("Running tests...", total=len(questions))
        
        results = []
        for q in questions:
            try:
                result = bench.run_single_test(
                    model_type=model_type,
                    model_key=model_key,
                    question=q,
                    max_pressure_rounds=pressure_level,
                    save_conversation=save_conversation
                )
                results.append(result)
                
                # Log result
                logger.log_test_complete(
                    model_key,
                    result.final_flip_status,
                    result.test_duration
                )
                
                # Display result
                console.print(f"[green]✓[/green] {q[:50]}... → {result.final_flip_status}")
                
            except Exception as e:
                console.print(f"[red]✗[/red] {q[:50]}... → Error: {str(e)}")
                logger.log_error(e, f"testing {q}")
            
            progress.update(task, advance=1)
    
    # Calculate and display statistics
    if results:
        test_results = [r.to_dict() for r in results]
        scorer = SycophancyScorer()
        scores = scorer.calculate_sycophancy_score(test_results)
        
        # Calculate total cost
        total_cost = sum(r.estimated_cost for r in results)
        total_input_tokens = sum(r.input_tokens for r in results)
        total_output_tokens = sum(r.output_tokens for r in results)
        
        console.print("\n[bold cyan]Results Summary:[/bold cyan]")
        console.print(f"Sycophancy Score: [bold]{scores['sycophancy_score']:.1f}[/bold] - {scores['interpretation']}")
        console.print(f"Resistance Score: {scores['resistance_score']:.1f}%")
        console.print(f"Explicit Flips: {scores['components']['explicit_flip_rate']:.1f}%")
        console.print(f"Soft Flips: {scores['components']['soft_flip_rate']:.1f}%")
        
        console.print("\n[bold cyan]Cost Summary:[/bold cyan]")
        console.print(f"Total Input Tokens: {total_input_tokens:,}")
        console.print(f"Total Output Tokens: {total_output_tokens:,}")
        console.print(f"Estimated Total Cost: [bold]${total_cost:.4f}[/bold]")
        
        # Save results if requested
        if output:
            output_data = {
                "model_type": model_type,
                "model_key": model_key,
                "timestamp": datetime.utcnow().isoformat(),
                "results": test_results,
                "scores": scores
            }
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            console.print(f"\n[green]Results saved to {output}[/green]")


@cli.command()
@click.option('--models', '-m', multiple=True, required=True, help='Models to benchmark (format: type:key)')
@click.option('--question-file', '-f', type=click.Path(exists=True), help='File with questions')
@click.option('--use-defaults', is_flag=True, help='Use default safety questions')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for results')
@click.option('--pressure-type', '-p', default=None, help='Pressure type to use (see list-pressure-types)')
def benchmark(
    models: Tuple[str, ...],
    question_file: Optional[str],
    use_defaults: bool,
    output_dir: Optional[str],
    pressure_type: Optional[str]
):
    """Run comparative benchmark across multiple models"""
    
    # Parse model specifications
    model_specs = []
    for model_str in models:
        if ':' not in model_str:
            console.print(f"[red]Error: Invalid model format '{model_str}'. Use type:key format.[/red]")
            sys.exit(1)
        model_type, model_key = model_str.split(':', 1)
        model_specs.append((model_type, model_key))
    
    # Get questions
    if question_file:
        with open(question_file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
    elif use_defaults:
        questions = config.safety_questions
    else:
        console.print("[red]Error: Either --question-file or --use-defaults must be specified[/red]")
        sys.exit(1)
    
    # Set output directory
    results_dir = Path(output_dir) if output_dir else config.results_dir
    
    # Initialize benchmark (no evaluation during testing)
    bench = SycoBench(results_dir=results_dir, use_model_eval=False)
    
    console.print(f"\n[bold cyan]Running comparative benchmark[/bold cyan]")
    console.print(f"Models: {', '.join([f'{t}:{k}' for t, k in model_specs])}")
    console.print(f"Questions: {len(questions)}\n")
    
    # Run benchmark with async parallelism (20-40x faster)
    try:
        result = bench.run_comparative_benchmark_async(
            models=model_specs,
            questions=questions,
            save_results=True,
            pressure_type=pressure_type,
            use_async=True  # Use async parallelism for speed
        )

        # Display results from new structure
        console.print("\n[bold green]✓ Experiment complete![/bold green]")
        console.print(f"Experiment ID: {result['experiment_id']}")
        console.print(f"Results saved to: {result['experiment_dir']}")

        # Display summary if available
        if "summary" in result:
            summary = result["summary"]

            # Display cost summary only (flip detection done later by scoring models)
            console.print("\n[bold cyan]Cost Summary:[/bold cyan]")
            console.print(f"Total Testing Cost: ${summary.get('total_testing_cost', 0):.4f}")

            console.print("\n[bold cyan]Per-Model Costs:[/bold cyan]")
            for model_key, model_data in summary.get("model_summaries", {}).items():
                console.print(f"{model_key}: ${model_data.get('total_cost', 0):.4f}")

        console.print(f"\n[green]Full results saved to {results_dir}[/green]")
        
    except Exception as e:
        console.print(f"[red]Benchmark failed: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('result_file', type=click.Path(exists=True))
def analyze(result_file: str):
    """Analyze saved benchmark results"""
    
    with open(result_file, 'r') as f:
        data = json.load(f)
    
    if "individual_results" in data:
        # Comparative benchmark result
        console.print("\n[bold cyan]Comparative Benchmark Analysis[/bold cyan]\n")
        
        for model_key, model_data in data["individual_results"].items():
            if "error" not in model_data:
                stats = model_data.get("statistics", {})
                console.print(f"[bold yellow]{model_key}:[/bold yellow]")
                console.print(f"  Safety Score: {stats.get('safety_score', 0):.1f}%")
                console.print(f"  Explicit Flips: {stats['flip_rates'].get('explicit_flip', 0):.1f}%")
                console.print(f"  Soft Flips: {stats['flip_rates'].get('soft_flip', 0):.1f}%")
                if stats.get('average_flip_level'):
                    console.print(f"  Avg Flip Level: {stats['average_flip_level']:.1f}")
                console.print()
    
    elif "results" in data:
        # Single model result
        model_info = f"{data.get('model_type', 'Unknown')}:{data.get('model_key', 'Unknown')}"
        console.print(f"\n[bold cyan]Analysis for {model_info}[/bold cyan]\n")
        
        if "scores" in data:
            scores = data["scores"]
            console.print(f"Sycophancy Score: [bold]{scores['sycophancy_score']:.1f}[/bold] - {scores['interpretation']}")
            console.print(f"Resistance Score: {scores['resistance_score']:.1f}%")
            
            # Show detailed breakdown
            console.print("\n[bold]Detailed Breakdown:[/bold]")
            for result in data["results"]:
                question = result["question"][:50] + "..." if len(result["question"]) > 50 else result["question"]
                console.print(f"• {question}")
                console.print(f"  Status: {result['final_flip_status']}")
                if result.get("pressure_results"):
                    for pr in result["pressure_results"]:
                        if pr["flip_type"] != "no_flip":
                            console.print(f"  Flip at level {pr['level']}: {pr['flip_type']}")


@cli.command()
def validate_env():
    """Validate environment setup and API keys"""
    console.print("\n[bold cyan]Validating Environment Setup[/bold cyan]\n")
    
    checks = [
        ("Anthropic API Key", bool(config.anthropic_api_key)),
        ("OpenAI API Key", bool(config.openai_api_key)),
        ("Google API Key", bool(config.gemini_api_key)),
        ("xAI API Key", bool(config.xai_api_key)),
        ("Results Directory", config.results_dir.exists()),
    ]
    
    all_good = True
    for check_name, status in checks:
        if status:
            console.print(f"[green]✓[/green] {check_name}")
        else:
            console.print(f"[red]✗[/red] {check_name}")
            all_good = False
    
    if all_good:
        console.print("\n[green]All checks passed! Environment is properly configured.[/green]")
    else:
        console.print("\n[yellow]Some checks failed. Please set up missing API keys in .env file.[/yellow]")
        console.print("Copy .env.example to .env and add your API keys.")


if __name__ == "__main__":
    cli()