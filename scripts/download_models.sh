#!/bin/bash
# ============================================
# Model Download Script
# Downloads Qwen3-ASR and IndexTTS2 models using HF-Mirror
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# Configuration
# ============================================
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
MODELS_DIR="${MODELS_DIR:-./models}"
CACHE_DIR="${CACHE_DIR:-$MODELS_DIR/.cache/huggingface}"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Model Download Script${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "HF_ENDPOINT: $HF_ENDPOINT"
echo "MODELS_DIR: $MODELS_DIR"
echo "CACHE_DIR: $CACHE_DIR"
echo ""

# ============================================
# Create directories
# ============================================
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$MODELS_DIR/qwen3-asr"
mkdir -p "$MODELS_DIR/indextts"
mkdir -p "$CACHE_DIR"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# ============================================
# Check if huggingface-cli is available
# ============================================
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${YELLOW}huggingface-cli not found, installing...${NC}"
    pip install -U huggingface-hub
fi

# ============================================
# Set HuggingFace environment variables
# ============================================
export HF_ENDPOINT="$HF_ENDPOINT"
export HUGGINGFACE_HUB_CACHE="$CACHE_DIR"

# ============================================
# Download Qwen3-ASR-0.6B
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Downloading Qwen3-ASR-0.6B${NC}"
echo -e "${GREEN}============================================${NC}"

QWEN_ASR_MODEL="Qwen/Qwen3-ASR-0.6B"
QWEN_ASR_DIR="$MODELS_DIR/qwen3-asr"

if [ -d "$QWEN_ASR_DIR" ] && [ "$(ls -A $QWEN_ASR_DIR)" ]; then
    echo -e "${YELLOW}Qwen3-ASR-0.6B already exists in $QWEN_ASR_DIR${NC}"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✓ Skipping Qwen3-ASR-0.6B download${NC}"
    else
        echo -e "${YELLOW}Downloading Qwen3-ASR-0.6B...${NC}"
        huggingface-cli download "$QWEN_ASR_MODEL" \
            --local-dir "$QWEN_ASR_DIR" \
            --local-dir-use-symlinks False \
            --resume-download
        echo -e "${GREEN}✓ Qwen3-ASR-0.6B downloaded successfully${NC}"
    fi
else
    echo -e "${YELLOW}Downloading Qwen3-ASR-0.6B...${NC}"
    huggingface-cli download "$QWEN_ASR_MODEL" \
        --local-dir "$QWEN_ASR_DIR" \
        --local-dir-use-symlinks False \
        --resume-download
    echo -e "${GREEN}✓ Qwen3-ASR-0.6B downloaded successfully${NC}"
fi
echo ""

# ============================================
# Download Qwen3-ForcedAligner-0.6B (Optional)
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Downloading Qwen3-ForcedAligner-0.6B (Optional)${NC}"
echo -e "${GREEN}============================================${NC}"

read -p "Do you want to download Qwen3-ForcedAligner-0.6B for timestamp generation? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    QWEN_ALIGNER_MODEL="Qwen/Qwen3-ForcedAligner-0.6B"
    QWEN_ALIGNER_DIR="$MODELS_DIR/qwen3-aligner"
    
    echo -e "${YELLOW}Downloading Qwen3-ForcedAligner-0.6B...${NC}"
    huggingface-cli download "$QWEN_ALIGNER_MODEL" \
        --local-dir "$QWEN_ALIGNER_DIR" \
        --local-dir-use-symlinks False \
        --resume-download
    echo -e "${GREEN}✓ Qwen3-ForcedAligner-0.6B downloaded successfully${NC}"
else
    echo -e "${YELLOW}Skipping Qwen3-ForcedAligner-0.6B download${NC}"
fi
echo ""

# ============================================
# Download IndexTTS2
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Downloading IndexTTS2${NC}"
echo -e "${GREEN}============================================${NC}"

INDEXTTS_MODEL="IndexTeam/IndexTTS2"
INDEXTTS_DIR="$MODELS_DIR/indextts"

if [ -d "$INDEXTTS_DIR" ] && [ "$(ls -A $INDEXTTS_DIR)" ]; then
    echo -e "${YELLOW}IndexTTS2 already exists in $INDEXTTS_DIR${NC}"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✓ Skipping IndexTTS2 download${NC}"
    else
        echo -e "${YELLOW}Downloading IndexTTS2...${NC}"
        huggingface-cli download "$INDEXTTS_MODEL" \
            --local-dir "$INDEXTTS_DIR" \
            --local-dir-use-symlinks False \
            --resume-download
        echo -e "${GREEN}✓ IndexTTS2 downloaded successfully${NC}"
    fi
else
    echo -e "${YELLOW}Downloading IndexTTS2...${NC}"
    huggingface-cli download "$INDEXTTS_MODEL" \
        --local-dir "$INDEXTTS_DIR" \
        --local-dir-use-symlinks False \
        --resume-download
    echo -e "${GREEN}✓ IndexTTS2 downloaded successfully${NC}"
fi
echo ""

# ============================================
# Verify downloads
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Verifying downloads${NC}"
echo -e "${GREEN}============================================${NC}"

verify_model() {
    local model_dir=$1
    local model_name=$2
    
    if [ -d "$model_dir" ] && [ "$(ls -A $model_dir)" ]; then
        local size=$(du -sh "$model_dir" | cut -f1)
        echo -e "${GREEN}✓ $model_name: $size${NC}"
        return 0
    else
        echo -e "${RED}✗ $model_name: Not found or empty${NC}"
        return 1
    fi
}

VERIFICATION_FAILED=0

verify_model "$QWEN_ASR_DIR" "Qwen3-ASR-0.6B" || VERIFICATION_FAILED=1
verify_model "$INDEXTTS_DIR" "IndexTTS2" || VERIFICATION_FAILED=1

if [ -d "$MODELS_DIR/qwen3-aligner" ]; then
    verify_model "$MODELS_DIR/qwen3-aligner" "Qwen3-ForcedAligner-0.6B" || VERIFICATION_FAILED=1
fi

echo ""

# ============================================
# Summary
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Download Summary${NC}"
echo -e "${GREEN}============================================${NC}"

if [ $VERIFICATION_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All models downloaded successfully!${NC}"
    echo ""
    echo "Models location: $MODELS_DIR"
    echo "Cache location: $CACHE_DIR"
    echo ""
    echo "You can now start the application with:"
    echo "  docker-compose up -d"
    echo "or"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 0
else
    echo -e "${RED}✗ Some models failed to download${NC}"
    echo "Please check the errors above and try again."
    exit 1
fi
