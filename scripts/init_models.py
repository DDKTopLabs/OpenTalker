#!/usr/bin/env python3
"""
Model Initialization Script
Downloads and verifies Qwen3-ASR and IndexTTS2 models using HF-Mirror
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from huggingface_hub import snapshot_download
    from tqdm import tqdm
except ImportError:
    print("Error: huggingface_hub not installed")
    print("Please install it: pip install huggingface-hub")
    sys.exit(1)


class ModelDownloader:
    """Model downloader with progress tracking and error handling"""

    def __init__(
        self,
        hf_endpoint: str = "https://hf-mirror.com",
        models_dir: str = "./models",
    ):
        self.hf_endpoint = hf_endpoint
        self.models_dir = Path(models_dir)
        self.cache_dir = self.models_dir / ".cache" / "huggingface"

        # Set environment variables
        os.environ["HF_ENDPOINT"] = self.hf_endpoint
        os.environ["HUGGINGFACE_HUB_CACHE"] = str(self.cache_dir)

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_model(
        self,
        repo_id: str,
        local_dir: Path,
        model_name: str,
        force: bool = False,
    ) -> bool:
        """
        Download a model from HuggingFace

        Args:
            repo_id: HuggingFace repository ID
            local_dir: Local directory to save model
            model_name: Human-readable model name
            force: Force re-download even if exists

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'=' * 60}")
        print(f"Downloading {model_name}")
        print(f"{'=' * 60}")
        print(f"Repository: {repo_id}")
        print(f"Local directory: {local_dir}")
        print()

        # Check if already exists
        if local_dir.exists() and any(local_dir.iterdir()) and not force:
            print(f"✓ {model_name} already exists")
            response = input("Re-download? (y/N): ").strip().lower()
            if response != "y":
                print(f"✓ Skipping {model_name}")
                return True

        # Create local directory
        local_dir.mkdir(parents=True, exist_ok=True)

        try:
            print(f"Downloading {model_name}...")
            print(f"Using mirror: {self.hf_endpoint}")

            # Download with progress bar
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
                resume_download=True,
                max_workers=4,
            )

            print(f"✓ {model_name} downloaded successfully")
            return True

        except KeyboardInterrupt:
            print(f"\n✗ Download interrupted by user")
            return False
        except Exception as e:
            print(f"✗ Failed to download {model_name}: {e}")
            return False

    def verify_model(self, model_dir: Path, model_name: str) -> bool:
        """
        Verify model download

        Args:
            model_dir: Model directory
            model_name: Model name

        Returns:
            True if valid, False otherwise
        """
        if not model_dir.exists():
            print(f"✗ {model_name}: Directory not found")
            return False

        if not any(model_dir.iterdir()):
            print(f"✗ {model_name}: Directory is empty")
            return False

        # Calculate size
        total_size = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        size_gb = size_mb / 1024

        if size_gb >= 1:
            size_str = f"{size_gb:.2f} GB"
        else:
            size_str = f"{size_mb:.2f} MB"

        print(f"✓ {model_name}: {size_str}")
        return True

    def download_all(self, include_aligner: bool = False) -> bool:
        """
        Download all required models

        Args:
            include_aligner: Whether to download forced aligner

        Returns:
            True if all downloads successful
        """
        print("=" * 60)
        print("Model Download Script")
        print("=" * 60)
        print(f"HF_ENDPOINT: {self.hf_endpoint}")
        print(f"MODELS_DIR: {self.models_dir}")
        print(f"CACHE_DIR: {self.cache_dir}")
        print()

        success = True

        # Download Qwen3-ASR-0.6B
        qwen_asr_dir = self.models_dir / "qwen3-asr"
        if not self.download_model(
            repo_id="Qwen/Qwen3-ASR-0.6B",
            local_dir=qwen_asr_dir,
            model_name="Qwen3-ASR-0.6B",
        ):
            success = False

        # Download Qwen3-ForcedAligner-0.6B (optional)
        if include_aligner:
            qwen_aligner_dir = self.models_dir / "qwen3-aligner"
            if not self.download_model(
                repo_id="Qwen/Qwen3-ForcedAligner-0.6B",
                local_dir=qwen_aligner_dir,
                model_name="Qwen3-ForcedAligner-0.6B",
            ):
                success = False

        # Download IndexTTS2
        indextts_dir = self.models_dir / "indextts"
        if not self.download_model(
            repo_id="IndexTeam/IndexTTS2",
            local_dir=indextts_dir,
            model_name="IndexTTS2",
        ):
            success = False

        # Verify all downloads
        print(f"\n{'=' * 60}")
        print("Verifying downloads")
        print(f"{'=' * 60}\n")

        verification_success = True
        verification_success &= self.verify_model(qwen_asr_dir, "Qwen3-ASR-0.6B")
        verification_success &= self.verify_model(indextts_dir, "IndexTTS2")

        if include_aligner:
            qwen_aligner_dir = self.models_dir / "qwen3-aligner"
            verification_success &= self.verify_model(qwen_aligner_dir, "Qwen3-ForcedAligner-0.6B")

        # Summary
        print(f"\n{'=' * 60}")
        print("Download Summary")
        print(f"{'=' * 60}\n")

        if success and verification_success:
            print("✓ All models downloaded successfully!")
            print()
            print(f"Models location: {self.models_dir}")
            print(f"Cache location: {self.cache_dir}")
            print()
            print("You can now start the application with:")
            print("  docker-compose up -d")
            print("or")
            print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
            return True
        else:
            print("✗ Some models failed to download or verify")
            print("Please check the errors above and try again.")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Download models for OpenAI-compatible Audio API")
    parser.add_argument(
        "--hf-endpoint",
        default=os.getenv("HF_ENDPOINT", "https://hf-mirror.com"),
        help="HuggingFace mirror endpoint",
    )
    parser.add_argument(
        "--models-dir",
        default=os.getenv("MODELS_DIR", "./models"),
        help="Models directory",
    )
    parser.add_argument(
        "--include-aligner",
        action="store_true",
        help="Download Qwen3-ForcedAligner-0.6B for timestamp generation",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if models exist",
    )

    args = parser.parse_args()

    # Create downloader
    downloader = ModelDownloader(
        hf_endpoint=args.hf_endpoint,
        models_dir=args.models_dir,
    )

    # Download all models
    success = downloader.download_all(include_aligner=args.include_aligner)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
