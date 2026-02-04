#!/bin/bash
# Test Gateway TTS Endpoint
# Tests the OpenAI-compatible /v1/audio/speech endpoint

set -e

GATEWAY_URL="http://localhost:8000"
OUTPUT_DIR="/tmp/gateway_tts_test"

echo "=========================================="
echo "Gateway TTS Endpoint Test"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Test 1: Chinese female voice (vivian)
echo "Test 1: Chinese female voice (vivian)"
curl -X POST "$GATEWAY_URL/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "你好世界，这是一个测试。",
    "voice": "vivian",
    "response_format": "wav",
    "speed": 1.0
  }' \
  -o "$OUTPUT_DIR/test1_chinese_vivian.wav" \
  --silent --show-error

if [ -f "$OUTPUT_DIR/test1_chinese_vivian.wav" ]; then
  SIZE=$(stat -f%z "$OUTPUT_DIR/test1_chinese_vivian.wav" 2>/dev/null || stat -c%s "$OUTPUT_DIR/test1_chinese_vivian.wav" 2>/dev/null)
  echo "✅ Success: $SIZE bytes"
else
  echo "❌ Failed: File not created"
fi
echo ""

# Test 2: English male voice (ryan)
echo "Test 2: English male voice (ryan)"
curl -X POST "$GATEWAY_URL/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "Hello world, this is a test.",
    "voice": "ryan",
    "response_format": "wav",
    "speed": 1.0
  }' \
  -o "$OUTPUT_DIR/test2_english_ryan.wav" \
  --silent --show-error

if [ -f "$OUTPUT_DIR/test2_english_ryan.wav" ]; then
  SIZE=$(stat -f%z "$OUTPUT_DIR/test2_english_ryan.wav" 2>/dev/null || stat -c%s "$OUTPUT_DIR/test2_english_ryan.wav" 2>/dev/null)
  echo "✅ Success: $SIZE bytes"
else
  echo "❌ Failed: File not created"
fi
echo ""

# Test 3: Chinese male voice (dylan)
echo "Test 3: Chinese male voice (dylan)"
curl -X POST "$GATEWAY_URL/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "欢迎使用OpenTalker语音合成服务。",
    "voice": "dylan",
    "response_format": "wav",
    "speed": 1.0
  }' \
  -o "$OUTPUT_DIR/test3_chinese_dylan.wav" \
  --silent --show-error

if [ -f "$OUTPUT_DIR/test3_chinese_dylan.wav" ]; then
  SIZE=$(stat -f%z "$OUTPUT_DIR/test3_chinese_dylan.wav" 2>/dev/null || stat -c%s "$OUTPUT_DIR/test3_chinese_dylan.wav" 2>/dev/null)
  echo "✅ Success: $SIZE bytes"
else
  echo "❌ Failed: File not created"
fi
echo ""

# Test 4: Speed adjustment (1.5x)
echo "Test 4: Speed adjustment (1.5x)"
curl -X POST "$GATEWAY_URL/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "这是一个快速语音测试。",
    "voice": "vivian",
    "response_format": "wav",
    "speed": 1.5
  }' \
  -o "$OUTPUT_DIR/test4_speed_1.5x.wav" \
  --silent --show-error

if [ -f "$OUTPUT_DIR/test4_speed_1.5x.wav" ]; then
  SIZE=$(stat -f%z "$OUTPUT_DIR/test4_speed_1.5x.wav" 2>/dev/null || stat -c%s "$OUTPUT_DIR/test4_speed_1.5x.wav" 2>/dev/null)
  echo "✅ Success: $SIZE bytes"
else
  echo "❌ Failed: File not created"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Output files:"
ls -lh "$OUTPUT_DIR"/*.wav 2>/dev/null || echo "No files created"
echo ""
echo "Test completed!"
echo "Files saved to: $OUTPUT_DIR"
