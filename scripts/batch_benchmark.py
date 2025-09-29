#!/usr/bin/env python3
"""
Unified batch benchmarking script for SycoBench.
Supports multiple providers and models for large-scale safety testing.
"""
import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print banner and information."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                 SycoBench Batch Benchmarking                  ║
║         Test 1000+ questions with 50-96% cost savings         ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def show_batch_options():
    """Show available batch options and pricing."""
    print("Available Batch Options:\n")
    
    print("1. OpenAI Batch API (50% discount, 24h turnaround)")
    print("   Models and costs (per 1000 questions with pressure testing):")
    print("   - gpt-4.1-nano:  ~$0.50 (was $1.00)")
    print("   - gpt-4.1-mini:  ~$2.00 (was $4.00)")
    print("   - gpt-4o-mini:   ~$0.75 (was $1.50)")
    print("   - gpt-3.5-turbo: ~$2.50 (was $5.00)")
    print("")
    
    print("2. Google Gemini Batch (via Vertex AI)")
    print("   Models and costs (per 1000 questions with pressure testing):")
    print("   - gemini-2.5-flash: ~$0.37")
    print("   - gemini-2.5-pro:   ~$12.50")
    print("   Note: Requires GCP project and bucket setup")
    print("")
    
    print("3. Anthropic Batch API")
    print("   Status: Not yet available")
    print("   Note: Anthropic has announced batch API coming soon")
    print("")

def create_batch_config():
    """Create configuration for batch jobs."""
    config = {
        "timestamp": datetime.now().isoformat(),
        "jobs": []
    }
    
    print("\nSelect providers to test (comma-separated numbers):")
    print("1. OpenAI")
    print("2. Google Gemini")
    print("3. Skip and see recommendations")
    
    selection = input("\nYour choice (e.g., 1,2): ").strip()
    
    if "3" in selection:
        show_recommendations()
        return None
    
    if "1" in selection:
        print("\nOpenAI Configuration:")
        print("Select models (comma-separated):")
        print("1. gpt-4.1-nano (cheapest)")
        print("2. gpt-4.1-mini")
        print("3. gpt-4.1")
        print("4. gpt-4o")
        print("5. gpt-4o-mini")
        print("6. gpt-3.5-turbo")
        print("7. o3 (reasoning)")
        print("8. o4-mini (reasoning)")
        
        model_selection = input("Your choice: ").strip()
        models = []
        if "1" in model_selection:
            models.append("gpt-4.1-nano")
        if "2" in model_selection:
            models.append("gpt-4.1-mini")
        if "3" in model_selection:
            models.append("gpt-4o-mini")
        if "4" in model_selection:
            models.append("gpt-3.5-turbo")
        
        for model in models:
            config["jobs"].append({
                "provider": "openai",
                "model": model,
                "questions": 1000,
                "status": "pending"
            })
    
    if "2" in selection:
        print("\nGoogle Gemini Configuration:")
        print("Prerequisites:")
        print("- export PROJECT_ID=your-gcp-project")
        print("- export BUCKET_NAME=your-gcs-bucket")
        print("")
        print("Select models:")
        print("1. gemini-2.5-flash (cheap & fast)")
        print("2. gemini-2.5-pro (expensive but powerful)")
        
        model_selection = input("Your choice: ").strip()
        models = []
        if "1" in model_selection:
            models.append("gemini-2.5-flash")
        if "2" in model_selection:
            models.append("gemini-2.5-pro")
        
        for model in models:
            config["jobs"].append({
                "provider": "gemini",
                "model": model,
                "questions": 1000,
                "status": "pending"
            })
    
    # Save config
    config_file = f"batch_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to: {config_file}")
    return config

def show_recommendations():
    """Show recommended batch jobs based on budget and goals."""
    print("\n" + "="*60)
    print("RECOMMENDED BATCH JOBS")
    print("="*60)
    
    print("\n1. BUDGET-CONSCIOUS COMPREHENSIVE TEST (~$0.87 total)")
    print("   Run these three for broad coverage at minimal cost:")
    print("   • OpenAI: gpt-4.1-nano ($0.50)")
    print("   • Gemini: gemini-2.5-flash ($0.37)")
    print("   • Regular API: claude-haiku-3.5 (use existing code)")
    print("")
    print("   Commands:")
    print("   python run_openai_batch.py gpt-4.1-nano")
    print("   ./run_gemini_batch.sh  # After setting PROJECT_ID and BUCKET_NAME")
    print("")
    
    print("2. OPENAI MODEL COMPARISON (~$3.25 total)")
    print("   Compare different OpenAI model sizes:")
    print("   • gpt-4.1-nano ($0.50)")
    print("   • gpt-4.1-mini ($2.00)")
    print("   • gpt-4o-mini ($0.75)")
    print("")
    print("   Commands:")
    print("   python run_openai_batch.py gpt-4.1-nano")
    print("   python run_openai_batch.py gpt-4.1-mini")
    print("   python run_openai_batch.py gpt-4o-mini")
    print("")
    
    print("3. ULTRA-LOW COST TEST (~$0.37 total)")
    print("   Just test Gemini 2.5 Flash:")
    print("   • Gemini: gemini-2.5-flash ($0.37)")
    print("")
    print("   Command:")
    print("   ./run_gemini_batch.sh")
    print("")
    
    print("4. HIGH-QUALITY COMPARISON (~$14.50 total)")
    print("   Compare top models from each provider:")
    print("   • OpenAI: gpt-4.1-mini ($2.00)")
    print("   • Gemini: gemini-2.5-pro ($12.50)")
    print("")
    
    print("\nNOTES:")
    print("- All batch jobs complete within 24 hours")
    print("- OpenAI batches are 50% cheaper than regular API")
    print("- Gemini batch pricing varies by region")
    print("- Results include full pressure testing (6 interactions per question)")
    print("- All costs shown are with batch discounts applied")

def check_batch_status():
    """Check status of all batch jobs."""
    print("\n" + "="*60)
    print("BATCH JOB STATUS")
    print("="*60)
    
    # Check for batch info files
    batch_info_files = []
    
    # Check tools directory
    tools_dir = Path("tools")
    if tools_dir.exists():
        batch_info_files.extend(tools_dir.glob("*batch_info.json"))
    
    # Check batch_data directory
    batch_data_dir = Path("batch_data")
    if batch_data_dir.exists():
        for provider in ["openai", "claude", "gemini"]:
            provider_dir = batch_data_dir / provider
            if provider_dir.exists():
                batch_info_files.extend(provider_dir.glob("*batch_info.json"))
                batch_info_files.extend(provider_dir.glob("*batch_status.json"))
    
    # Also check for config files
    config_files = list(Path(".").glob("batch_config_*.json"))
    
    if not batch_info_files and not config_files:
        print("\n❌ No batch jobs found")
        print("\nTo create a new batch job, run:")
        print("  python batch_benchmark.py")
        return
    
    # Display batch jobs
    print("\n📋 Found Batch Jobs:\n")
    
    # Process batch info files
    active_batches = []
    completed_batches = []
    
    for info_file in batch_info_files:
        try:
            with open(info_file, 'r') as f:
                info = json.load(f)
            
            provider = "unknown"
            if "claude" in str(info_file).lower():
                provider = "claude"
            elif "openai" in str(info_file).lower():
                provider = "openai"
            elif "gemini" in str(info_file).lower():
                provider = "gemini"
            
            batch_info = {
                "provider": provider,
                "file": info_file,
                "data": info
            }
            
            # Check if results exist
            batch_id = info.get("batch_id", "")
            results_patterns = [
                f"*{batch_id}*.jsonl",
                f"*{batch_id}*results*.json",
                f"*{batch_id}*analysis*.json"
            ]
            
            has_results = False
            for pattern in results_patterns:
                if list(info_file.parent.glob(pattern)):
                    has_results = True
                    break
            
            if has_results:
                completed_batches.append(batch_info)
            else:
                active_batches.append(batch_info)
                
        except Exception as e:
            print(f"⚠️  Error reading {info_file}: {e}")
    
    # Display active batches
    if active_batches:
        print("🔄 ACTIVE BATCHES:")
        for batch in active_batches:
            info = batch["data"]
            print(f"\n  Provider: {batch['provider'].upper()}")
            print(f"  Batch ID: {info.get('batch_id', 'N/A')}")
            print(f"  Model: {info.get('model', 'N/A')}")
            print(f"  Created: {info.get('created_at', 'N/A')}")
            print(f"  Requests: {info.get('total_requests', 'N/A')}")
            print(f"  File: {batch['file']}")
            
            # Provider-specific instructions
            if batch['provider'] == 'openai':
                print(f"\n  Check status: python src/batch/batch_manager.py --provider openai --action check --batch-id {info.get('batch_id')}")
                print(f"  Monitor: python src/batch/batch_manager.py --provider openai --action monitor --batch-id {info.get('batch_id')}")
            elif batch['provider'] == 'claude':
                print(f"\n  Check status: python src/batch/batch_manager.py --provider claude --action check --batch-id {info.get('batch_id')}")
                print(f"  Monitor: python src/batch/batch_manager.py --provider claude --action monitor --batch-id {info.get('batch_id')}")
            elif batch['provider'] == 'gemini':
                print(f"\n  Check status: Use Google Cloud Console or gcloud CLI")
    
    # Display completed batches
    if completed_batches:
        print("\n\n✅ COMPLETED BATCHES:")
        for batch in completed_batches:
            info = batch["data"]
            print(f"\n  Provider: {batch['provider'].upper()}")
            print(f"  Batch ID: {info.get('batch_id', 'N/A')}")
            print(f"  Model: {info.get('model', 'N/A')}")
            print(f"  Results available in: {batch['file'].parent}")
    
    # Display batch configs
    if config_files:
        print("\n\n📄 BATCH CONFIGURATIONS:")
        for config_file in sorted(config_files, reverse=True)[:5]:  # Show last 5
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                print(f"\n  File: {config_file}")
                print(f"  Created: {config.get('timestamp', 'N/A')}")
                print(f"  Jobs: {len(config.get('jobs', []))}")
                
                for job in config.get('jobs', []):
                    print(f"    - {job['provider']}: {job['model']} ({job['questions']} questions)")
                    
            except Exception as e:
                print(f"  ⚠️  Error reading {config_file}: {e}")
    
    print("\n" + "="*60)
    print("\n💡 Tips:")
    print("- Use batch_manager.py to check and monitor specific batches")
    print("- Results are automatically downloaded when batches complete")
    print("- Process results with batch_processor.py")
    print("- Create new batches with: python batch_benchmark.py")

def main():
    """Main entry point."""
    print_banner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "recommend":
            show_recommendations()
        elif sys.argv[1] == "status":
            check_batch_status()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python batch_benchmark.py [recommend|status]")
    else:
        show_batch_options()
        config = create_batch_config()
        if config:
            print("\nNext steps:")
            print("1. Review the configuration file")
            print("2. Run individual batch jobs as shown above")
            print("3. Monitor progress and download results")
            print("4. Process results with respective analysis scripts")

if __name__ == "__main__":
    main()