#!/usr/bin/env python3
"""
Unified batch manager for all SycoBench providers.
Consolidates functionality from run_openai_batch.py and run_claude_batch.py.
"""

import json
import time
import argparse
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class BatchManager:
    """Unified batch manager supporting all SycoBench providers."""
    
    def __init__(self):
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize API clients for all providers."""
        try:
            import openai
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.clients["openai"] = openai.OpenAI(api_key=openai_key)
        except ImportError:
            pass
        
        try:
            import anthropic
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            if claude_key:
                self.clients["claude"] = anthropic.Anthropic(api_key=claude_key)
        except ImportError:
            pass
        
        try:
            import google.generativeai as genai
            google_key = os.getenv("GEMINI_API_KEY")
            if google_key:
                genai.configure(api_key=google_key)
                self.clients["gemini"] = genai
        except ImportError:
            pass
    
    def create_batch(self, provider: str, input_file: str, description: str = "") -> str:
        """Create a batch job for the specified provider."""
        if provider not in self.clients:
            raise ValueError(f"Client not available for provider: {provider}")
        
        if provider == "openai":
            return self._create_openai_batch(input_file, description)
        elif provider == "claude":
            return self._create_claude_batch(input_file, description)
        elif provider == "gemini":
            return self._create_gemini_batch(input_file, description)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_openai_batch(self, input_file: str, description: str) -> str:
        """Create OpenAI batch job."""
        client = self.clients["openai"]
        
        # Upload file
        with open(input_file, 'rb') as f:
            file_response = client.files.create(
                file=f,
                purpose="batch"
            )
        
        # Create batch
        batch_response = client.batches.create(
            input_file_id=file_response.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": description}
        )
        
        print(f"✅ OpenAI batch created: {batch_response.id}")
        print(f"📁 Input file ID: {file_response.id}")
        print(f"⏱️  Completion window: 24h")
        
        return batch_response.id
    
    def _create_claude_batch(self, input_file: str, description: str) -> str:
        """Create Claude batch job."""
        client = self.clients["claude"]
        
        # Read batch requests
        with open(input_file, 'r') as f:
            requests = [json.loads(line) for line in f]
        
        # Create batch
        batch_response = client.messages.batches.create(requests=requests)
        
        print(f"✅ Claude batch created: {batch_response.id}")
        print(f"📊 Requests: {len(requests)}")
        print(f"📈 Status: {batch_response.processing_status}")
        
        return batch_response.id
    
    def _create_gemini_batch(self, input_file: str, description: str) -> str:
        """Create Gemini batch job (requires Vertex AI)."""
        print("⚠️  Gemini batch processing requires Vertex AI setup")
        print("   Use the shell script: run_gemini_batch.sh")
        print("   Or set up Vertex AI batch prediction directly")
        
        # For now, return a placeholder
        return "gemini_batch_placeholder"
    
    def check_status(self, provider: str, batch_id: str) -> Dict[str, Any]:
        """Check batch job status."""
        if provider not in self.clients:
            raise ValueError(f"Client not available for provider: {provider}")
        
        if provider == "openai":
            return self._check_openai_status(batch_id)
        elif provider == "claude":
            return self._check_claude_status(batch_id)
        elif provider == "gemini":
            return self._check_gemini_status(batch_id)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _check_openai_status(self, batch_id: str) -> Dict[str, Any]:
        """Check OpenAI batch status."""
        client = self.clients["openai"]
        batch = client.batches.retrieve(batch_id)
        
        return {
            "id": batch.id,
            "status": batch.status,
            "created_at": batch.created_at,
            "completed_at": batch.completed_at,
            "failed_at": batch.failed_at,
            "request_counts": batch.request_counts,
            "output_file_id": batch.output_file_id,
            "error_file_id": batch.error_file_id
        }
    
    def _check_claude_status(self, batch_id: str) -> Dict[str, Any]:
        """Check Claude batch status."""
        client = self.clients["claude"]
        batch = client.messages.batches.retrieve(batch_id)
        
        return {
            "id": batch.id,
            "processing_status": batch.processing_status,
            "created_at": batch.created_at,
            "expires_at": batch.expires_at,
            "request_counts": batch.request_counts,
            "results_url": getattr(batch, 'results_url', None)
        }
    
    def _check_gemini_status(self, batch_id: str) -> Dict[str, Any]:
        """Check Gemini batch status."""
        return {
            "id": batch_id,
            "status": "unknown",
            "message": "Use Vertex AI console or gcloud CLI to check status"
        }
    
    def download_results(self, provider: str, batch_id: str, output_file: str) -> bool:
        """Download batch results."""
        if provider not in self.clients:
            raise ValueError(f"Client not available for provider: {provider}")
        
        if provider == "openai":
            return self._download_openai_results(batch_id, output_file)
        elif provider == "claude":
            return self._download_claude_results(batch_id, output_file)
        elif provider == "gemini":
            return self._download_gemini_results(batch_id, output_file)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _download_openai_results(self, batch_id: str, output_file: str) -> bool:
        """Download OpenAI batch results."""
        client = self.clients["openai"]
        
        # Get batch info
        batch = client.batches.retrieve(batch_id)
        
        if batch.status != "completed":
            print(f"❌ Batch not completed yet. Status: {batch.status}")
            return False
        
        if not batch.output_file_id:
            print("❌ No output file available")
            return False
        
        # Download results
        file_response = client.files.content(batch.output_file_id)
        
        with open(output_file, 'wb') as f:
            f.write(file_response.content)
        
        print(f"✅ Results downloaded: {output_file}")
        return True
    
    def _download_claude_results(self, batch_id: str, output_file: str) -> bool:
        """Download Claude batch results."""
        client = self.clients["claude"]
        
        # Get batch info
        batch = client.messages.batches.retrieve(batch_id)
        
        if batch.processing_status != "ended":
            print(f"❌ Batch not completed yet. Status: {batch.processing_status}")
            return False
        
        # Get results
        results = client.messages.batches.results(batch_id)
        
        with open(output_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result.to_dict()) + '\n')
        
        print(f"✅ Results downloaded: {output_file}")
        return True
    
    def _download_gemini_results(self, batch_id: str, output_file: str) -> bool:
        """Download Gemini batch results."""
        print("⚠️  Gemini results download requires Vertex AI setup")
        print("   Use gcloud CLI or Vertex AI console")
        return False
    
    def monitor_batch(self, provider: str, batch_id: str, check_interval: int = 60) -> None:
        """Monitor batch job until completion."""
        print(f"🔍 Monitoring {provider} batch: {batch_id}")
        print(f"⏰ Check interval: {check_interval} seconds")
        print("-" * 50)
        
        while True:
            try:
                status = self.check_status(provider, batch_id)
                
                if provider == "openai":
                    current_status = status["status"]
                    print(f"📊 Status: {current_status}")
                    
                    if "request_counts" in status and status["request_counts"]:
                        counts = status["request_counts"]
                        print(f"   Total: {counts.get('total', 0)}")
                        print(f"   Completed: {counts.get('completed', 0)}")
                        print(f"   Failed: {counts.get('failed', 0)}")
                    
                    if current_status in ["completed", "failed", "expired", "cancelled"]:
                        print(f"✅ Batch {current_status}")
                        break
                
                elif provider == "claude":
                    current_status = status["processing_status"]
                    print(f"📊 Status: {current_status}")
                    
                    if "request_counts" in status and status["request_counts"]:
                        counts = status["request_counts"]
                        print(f"   Processing: {counts.get('processing', 0)}")
                        print(f"   Succeeded: {counts.get('succeeded', 0)}")
                        print(f"   Errored: {counts.get('errored', 0)}")
                    
                    if current_status == "ended":
                        print("✅ Batch completed")
                        break
                
                print(f"⏳ Waiting {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error checking status: {e}")
                time.sleep(check_interval)

def main():
    parser = argparse.ArgumentParser(description="Manage batch jobs for SycoBench providers")
    parser.add_argument("--provider", required=True, choices=["openai", "claude", "gemini"],
                       help="Provider to use")
    parser.add_argument("--action", required=True, choices=["create", "check", "download", "monitor"],
                       help="Action to perform")
    parser.add_argument("--input", help="Input file for batch creation")
    parser.add_argument("--batch-id", help="Batch ID for check/download/monitor")
    parser.add_argument("--output", help="Output file for results download")
    parser.add_argument("--description", default="", help="Description for batch job")
    parser.add_argument("--interval", type=int, default=60, help="Check interval for monitoring")
    
    args = parser.parse_args()
    
    manager = BatchManager()
    
    if args.action == "create":
        if not args.input:
            print("❌ --input required for create action")
            return
        
        batch_id = manager.create_batch(args.provider, args.input, args.description)
        print(f"📋 Batch ID: {batch_id}")
        
    elif args.action == "check":
        if not args.batch_id:
            print("❌ --batch-id required for check action")
            return
        
        status = manager.check_status(args.provider, args.batch_id)
        print(f"📊 Batch Status for {args.batch_id}:")
        print(json.dumps(status, indent=2, default=str))
        
    elif args.action == "download":
        if not args.batch_id or not args.output:
            print("❌ --batch-id and --output required for download action")
            return
        
        success = manager.download_results(args.provider, args.batch_id, args.output)
        if not success:
            print("❌ Download failed")
        
    elif args.action == "monitor":
        if not args.batch_id:
            print("❌ --batch-id required for monitor action")
            return
        
        manager.monitor_batch(args.provider, args.batch_id, args.interval)

if __name__ == "__main__":
    main()