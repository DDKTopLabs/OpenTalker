## ADDED Requirements

### Requirement: Memory-Constrained Model Loading
The system SHALL manage model loading and unloading to operate within a 4GB VRAM constraint.

#### Scenario: Single model loaded at a time
- **WHEN** the system needs to load a model
- **THEN** the system SHALL ensure only one model (STT or TTS) is loaded in GPU memory at any time

#### Scenario: VRAM usage monitoring
- **WHEN** a model is loaded
- **THEN** the system SHALL monitor and report current VRAM usage

#### Scenario: VRAM limit enforcement
- **WHEN** VRAM usage approaches 4GB
- **THEN** the system SHALL prevent loading additional models and return an error

### Requirement: Automatic Model Switching
The system SHALL automatically load and unload models based on incoming API requests.

#### Scenario: STT request triggers model switch
- **WHEN** a client sends an STT request and the TTS model is currently loaded
- **THEN** the system SHALL unload the TTS model, load the STT model, and process the request

#### Scenario: TTS request triggers model switch
- **WHEN** a client sends a TTS request and the STT model is currently loaded
- **THEN** the system SHALL unload the STT model, load the TTS model, and process the request

#### Scenario: Same model already loaded
- **WHEN** a client sends a request for a model that is already loaded
- **THEN** the system SHALL process the request immediately without model switching

#### Scenario: Model switch timeout
- **WHEN** model switching takes longer than 30 seconds
- **THEN** the system SHALL timeout and return a 503 Service Unavailable error

### Requirement: Clean Model Unloading
The system SHALL properly release GPU memory when unloading models.

#### Scenario: Model unload releases memory
- **WHEN** the system unloads a model
- **THEN** the system SHALL call `torch.cuda.empty_cache()` to release GPU memory

#### Scenario: Memory verification after unload
- **WHEN** a model is unloaded
- **THEN** the system SHALL verify that VRAM usage has decreased by at least 80% of the model's size

#### Scenario: Graceful unload on errors
- **WHEN** an error occurs during model usage
- **THEN** the system SHALL still properly unload the model and release resources

### Requirement: Model State Tracking
The system SHALL maintain accurate state information about loaded models.

#### Scenario: Current model tracking
- **WHEN** a model is loaded or unloaded
- **THEN** the system SHALL update the current model state (STT, TTS, or NONE)

#### Scenario: Model state query
- **WHEN** a health check or status endpoint is called
- **THEN** the system SHALL report which model is currently loaded

#### Scenario: Loading state indication
- **WHEN** a model is being loaded or unloaded
- **THEN** the system SHALL indicate the model is in a transitional state

### Requirement: Concurrent Request Handling
The system SHALL queue requests during model switching to prevent race conditions.

#### Scenario: Request queuing during switch
- **WHEN** a model switch is in progress and a new request arrives
- **THEN** the system SHALL queue the request until the switch completes

#### Scenario: Queue processing order
- **WHEN** multiple requests are queued
- **THEN** the system SHALL process them in FIFO (first-in-first-out) order

#### Scenario: Queue timeout
- **WHEN** a queued request waits longer than 60 seconds
- **THEN** the system SHALL return a 503 Service Unavailable error for that request

### Requirement: Model Preloading Configuration
The system SHALL support optional model preloading at startup.

#### Scenario: No preload (default)
- **WHEN** the system starts with `ENABLE_MODEL_PRELOAD=false`
- **THEN** the system SHALL not load any models until the first request

#### Scenario: STT preload
- **WHEN** the system starts with `DEFAULT_PRELOAD_MODEL=stt`
- **THEN** the system SHALL load the STT model during startup

#### Scenario: TTS preload
- **WHEN** the system starts with `DEFAULT_PRELOAD_MODEL=tts`
- **THEN** the system SHALL load the TTS model during startup

### Requirement: Model Loading Performance
The system SHALL load models within acceptable time limits.

#### Scenario: STT model load time
- **WHEN** the system loads the Qwen3-ASR-0.6B model
- **THEN** the loading SHALL complete within 8 seconds

#### Scenario: TTS model load time
- **WHEN** the system loads the IndexTTS2 model
- **THEN** the loading SHALL complete within 6 seconds

#### Scenario: Model switch total time
- **WHEN** the system switches from one model to another
- **THEN** the total switch time (unload + load) SHALL not exceed 15 seconds

### Requirement: Error Recovery
The system SHALL recover gracefully from model loading failures.

#### Scenario: Load failure recovery
- **WHEN** a model fails to load due to insufficient memory
- **THEN** the system SHALL retry after clearing GPU cache

#### Scenario: Corrupted model handling
- **WHEN** a model file is corrupted or missing
- **THEN** the system SHALL return a clear error message and attempt to re-download the model

#### Scenario: Service availability during errors
- **WHEN** one model fails to load
- **THEN** the system SHALL still be able to serve requests for the other model type
