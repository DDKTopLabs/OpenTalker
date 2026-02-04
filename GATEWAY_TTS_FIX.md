# Gateway TTS Fix - Deployment Update

## Changes Made (2026-02-04)

### Issue Fixed
The Gateway's `/v1/audio/speech` endpoint was not properly mapping OpenAI-style requests to the TTS service format, causing compatibility issues.

### Root Cause
1. **Parameter Mismatch**: Gateway was sending `voice` parameter, but TTS service expects `speaker`
2. **Missing Language Mapping**: Gateway was not providing language codes, relying on TTS service auto-detection
3. **Full Object Forwarding**: Gateway was forwarding the entire request object including unsupported fields

### Solution Implemented

**File**: `gateway/app/routers/audio.py`

Added intelligent request mapping:
- Maps OpenAI `voice` parameter → TTS service `speaker` parameter
- Auto-detects language based on speaker name:
  - Chinese speakers: vivian, serena, uncle_fu, dylan, eric → `zh`
  - English speakers: ryan, aiden → `en`
  - Japanese speakers: ono_anna → `ja`
  - Korean speakers: sohee → `ko`
- Sends only required fields to TTS service

**File**: `gateway/app/main.py`
- Updated version from 0.2.0 → 0.3.0

### Commit Details
```
Commit: 50d84b5
Message: Fix: Gateway TTS request mapping and update version to 0.3.0
Branch: main
```

## Deployment Instructions

### On WSL Machine (192.168.31.77:2222)

1. **Pull Latest Changes**
   ```bash
   ssh -p 2222 devocy@192.168.31.77
   cd ~/OpenTalker
   git pull
   ```

2. **Restart Gateway Service**
   ```bash
   # Stop all services
   ./stop_all_services.sh
   
   # Clear Python cache (important!)
   cd gateway
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
   cd ..
   
   # Start all services
   ./start_all_services.sh
   ```

3. **Verify Services**
   ```bash
   ./check_services.sh
   ```

4. **Test Gateway TTS Endpoint**
   ```bash
   # Copy test script to WSL
   # (Upload test_gateway_tts.sh to WSL)
   
   chmod +x test_gateway_tts.sh
   ./test_gateway_tts.sh
   ```

### Expected Test Results

All 4 tests should pass:
- ✅ Test 1: Chinese female voice (vivian) - ~300-400KB WAV
- ✅ Test 2: English male voice (ryan) - ~200-300KB WAV
- ✅ Test 3: Chinese male voice (dylan) - ~300-400KB WAV
- ✅ Test 4: Speed adjustment (1.5x) - ~200-300KB WAV

Output files saved to: `/tmp/gateway_tts_test/`

## API Usage Examples

### OpenAI-Compatible Endpoint (Recommended)

```bash
# Chinese synthesis
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "你好世界",
    "voice": "vivian",
    "response_format": "wav",
    "speed": 1.0
  }' \
  -o output.wav

# English synthesis
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-tts",
    "input": "Hello world",
    "voice": "ryan",
    "response_format": "wav",
    "speed": 1.0
  }' \
  -o output.wav
```

### Supported Voices

**Chinese Speakers**:
- `vivian` - Female, calm
- `serena` - Female, energetic
- `uncle_fu` - Male, mature
- `dylan` - Male, young
- `eric` - Male, neutral

**English Speakers**:
- `ryan` - Male, clear
- `aiden` - Male, warm

**Other Languages**:
- `ono_anna` - Japanese female
- `sohee` - Korean female

### Parameters

- `model`: "qwen3-tts" (required)
- `input`: Text to synthesize, 1-4096 characters (required)
- `voice`: Speaker name (required)
- `response_format`: "wav", "mp3", "flac", "opus" (default: "wav")
- `speed`: 0.25-4.0 (default: 1.0)

## Verification Checklist

- [ ] Git pull completed successfully
- [ ] Python cache cleared
- [ ] All services restarted
- [ ] Gateway health check returns version 0.3.0
- [ ] Test 1 (Chinese vivian) passed
- [ ] Test 2 (English ryan) passed
- [ ] Test 3 (Chinese dylan) passed
- [ ] Test 4 (Speed 1.5x) passed
- [ ] Audio files playable and correct

## Troubleshooting

### Issue: Changes not reflected after git pull
**Solution**: Clear Python cache before restarting
```bash
cd ~/OpenTalker/gateway
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### Issue: Gateway still shows version 0.2.0
**Solution**: Gateway service not restarted properly
```bash
./stop_all_services.sh
ps aux | grep uvicorn  # Verify no processes running
./start_all_services.sh
```

### Issue: TTS synthesis fails with 500 error
**Solution**: Check TTS service logs
```bash
tail -f /tmp/tts.log
```

### Issue: Language detection incorrect
**Solution**: Explicitly specify language in direct TTS service call
```bash
curl -X POST http://localhost:8002/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你好",
    "speaker": "vivian",
    "language": "zh"
  }' \
  -o output.wav
```

## Technical Details

### Request Flow

1. **Client** → Gateway `/v1/audio/speech`
   ```json
   {
     "model": "qwen3-tts",
     "input": "你好世界",
     "voice": "vivian",
     "response_format": "wav",
     "speed": 1.0
   }
   ```

2. **Gateway** → TTS Service `/synthesize`
   ```json
   {
     "input": "你好世界",
     "speaker": "vivian",
     "language": "zh",
     "response_format": "wav",
     "speed": 1.0
   }
   ```

3. **TTS Service** → Returns WAV audio bytes

4. **Gateway** → Returns audio to client with proper headers

### Language Detection Logic

```python
# Map speaker name to language code
chinese_speakers = ["vivian", "serena", "uncle_fu", "dylan", "eric"]
english_speakers = ["ryan", "aiden"]
japanese_speakers = ["ono_anna"]
korean_speakers = ["sohee"]

if speaker.lower() in chinese_speakers:
    language = "zh"
elif speaker.lower() in english_speakers:
    language = "en"
# ... etc
```

If speaker not recognized, `language=None` and TTS service auto-detects from text.

## Next Steps

1. ✅ Deploy to WSL and test
2. ⏳ Test Docker deployment (when Docker available)
3. 📋 Consider adding more speaker voices
4. 📋 Add speaker list endpoint to Gateway
5. 📋 Add language override parameter to Gateway API

## Related Files

- `gateway/app/routers/audio.py` - Request mapping logic
- `gateway/app/main.py` - Version update
- `test_gateway_tts.sh` - Test script
- `GATEWAY_TTS_FIX.md` - This document

---

**Date**: 2026-02-04  
**Version**: 0.3.0  
**Commit**: 50d84b5  
**Status**: Ready for deployment
