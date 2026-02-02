## ADDED Requirements

### Requirement: OpenAI API Compatibility
The system SHALL provide a `/v1/audio/transcriptions` endpoint that is fully compatible with the OpenAI Whisper API specification.

#### Scenario: API endpoint exists
- **WHEN** a client sends a POST request to `/v1/audio/transcriptions`
- **THEN** the system responds with a valid HTTP response

#### Scenario: Request format matches OpenAI
- **WHEN** a client sends a multipart/form-data request with `file` and `model` fields
- **THEN** the system accepts and processes the request without errors

#### Scenario: Response format matches OpenAI
- **WHEN** transcription completes successfully
- **THEN** the system returns a JSON response with `text`, `language`, and `duration` fields

### Requirement: Audio Format Support
The system SHALL accept audio files in multiple formats including MP3, WAV, FLAC, M4A, OGG, and WEBM.

#### Scenario: MP3 file upload
- **WHEN** a client uploads an MP3 audio file
- **THEN** the system successfully transcribes the audio

#### Scenario: WAV file upload
- **WHEN** a client uploads a WAV audio file
- **THEN** the system successfully transcribes the audio

#### Scenario: Unsupported format rejection
- **WHEN** a client uploads a file with an unsupported format
- **THEN** the system returns a 400 Bad Request error with a descriptive message

### Requirement: Language Detection
The system SHALL automatically detect the spoken language from the audio input and return the detected language code.

#### Scenario: Chinese audio detection
- **WHEN** a client uploads Chinese audio without specifying a language
- **THEN** the system detects and returns language code "zh" or "Chinese"

#### Scenario: English audio detection
- **WHEN** a client uploads English audio without specifying a language
- **THEN** the system detects and returns language code "en" or "English"

#### Scenario: Manual language specification
- **WHEN** a client specifies a language parameter in the request
- **THEN** the system uses the specified language for transcription optimization

### Requirement: Timestamp Generation
The system SHALL support optional word-level and segment-level timestamp generation when requested.

#### Scenario: Segment timestamps requested
- **WHEN** a client requests `timestamp_granularities[]=segment`
- **THEN** the system returns segments with `start` and `end` timestamps

#### Scenario: Word timestamps requested
- **WHEN** a client requests `timestamp_granularities[]=word` and ForcedAligner is enabled
- **THEN** the system returns word-level timestamps with `word`, `start`, and `end` fields

#### Scenario: No timestamps requested
- **WHEN** a client does not request timestamps
- **THEN** the system returns only the transcribed text without timestamp data

### Requirement: Response Format Options
The system SHALL support multiple response formats including JSON, text, SRT, and VTT.

#### Scenario: JSON format (default)
- **WHEN** a client requests transcription without specifying response_format
- **THEN** the system returns a JSON response with structured data

#### Scenario: Plain text format
- **WHEN** a client specifies `response_format=text`
- **THEN** the system returns only the transcribed text as plain text

#### Scenario: SRT subtitle format
- **WHEN** a client specifies `response_format=srt`
- **THEN** the system returns transcription in SRT subtitle format with timestamps

#### Scenario: VTT subtitle format
- **WHEN** a client specifies `response_format=vtt`
- **THEN** the system returns transcription in WebVTT subtitle format

### Requirement: File Size Limits
The system SHALL enforce a maximum file size limit of 50MB for uploaded audio files.

#### Scenario: File within size limit
- **WHEN** a client uploads an audio file smaller than 50MB
- **THEN** the system accepts and processes the file

#### Scenario: File exceeds size limit
- **WHEN** a client uploads an audio file larger than 50MB
- **THEN** the system returns a 413 Payload Too Large error

### Requirement: Error Handling
The system SHALL provide clear error messages for common failure scenarios.

#### Scenario: Missing required file
- **WHEN** a client sends a request without the required `file` field
- **THEN** the system returns a 400 Bad Request error with message "Missing required field: file"

#### Scenario: Invalid audio file
- **WHEN** a client uploads a corrupted or invalid audio file
- **THEN** the system returns a 400 Bad Request error with a descriptive message

#### Scenario: Model loading failure
- **WHEN** the STT model fails to load due to insufficient resources
- **THEN** the system returns a 503 Service Unavailable error with retry information

### Requirement: Multilingual Support
The system SHALL support transcription for 52 languages and dialects as provided by Qwen3-ASR.

#### Scenario: Major language support
- **WHEN** a client uploads audio in Chinese, English, Japanese, Korean, French, German, Spanish, or Russian
- **THEN** the system successfully transcribes the audio with high accuracy

#### Scenario: Dialect support
- **WHEN** a client uploads audio in Chinese dialects (Cantonese, Wu, Minnan, etc.)
- **THEN** the system successfully transcribes the audio and identifies the dialect

#### Scenario: Language identification accuracy
- **WHEN** the system detects a language
- **THEN** the language identification accuracy SHALL be at least 95% for the supported languages
