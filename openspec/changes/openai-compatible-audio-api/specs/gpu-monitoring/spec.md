## ADDED Requirements

### Requirement: Real-Time VRAM Monitoring
The system SHALL provide real-time monitoring of GPU memory usage.

#### Scenario: VRAM usage query
- **WHEN** the system queries GPU memory status
- **THEN** the system SHALL return allocated, reserved, and free VRAM in gigabytes

#### Scenario: Continuous monitoring
- **WHEN** models are loaded or unloaded
- **THEN** the system SHALL update VRAM usage metrics immediately

#### Scenario: Multiple GPU handling
- **WHEN** multiple GPUs are available
- **THEN** the system SHALL monitor the GPU specified by CUDA_VISIBLE_DEVICES

### Requirement: Model Switch Performance Tracking
The system SHALL track and report performance metrics for model switching operations.

#### Scenario: Switch time recording
- **WHEN** a model switch occurs
- **THEN** the system SHALL record the total time taken for the switch

#### Scenario: Switch count tracking
- **WHEN** model switches occur
- **THEN** the system SHALL maintain a count of total switches since startup

#### Scenario: Average switch time calculation
- **WHEN** performance statistics are requested
- **THEN** the system SHALL calculate and return the average model switch time

### Requirement: Health Check Integration
The system SHALL expose GPU and model status through health check endpoints.

#### Scenario: Health endpoint includes GPU status
- **WHEN** a client calls the `/health` endpoint
- **THEN** the response SHALL include current VRAM usage and available memory

#### Scenario: Health endpoint includes model status
- **WHEN** a client calls the `/health` endpoint
- **THEN** the response SHALL include which model is currently loaded (STT, TTS, or NONE)

#### Scenario: Health check failure on GPU issues
- **WHEN** GPU memory is critically low (>95% used)
- **THEN** the health check SHALL return an unhealthy status

### Requirement: Performance Metrics Endpoint
The system SHALL provide a dedicated endpoint for detailed performance metrics.

#### Scenario: Metrics endpoint exists
- **WHEN** a client calls the `/metrics` or `/stats` endpoint
- **THEN** the system SHALL return detailed performance statistics

#### Scenario: Metrics include switch statistics
- **WHEN** metrics are requested
- **THEN** the response SHALL include total switches, average switch time, and last switch time

#### Scenario: Metrics include memory statistics
- **WHEN** metrics are requested
- **THEN** the response SHALL include current, peak, and average VRAM usage

### Requirement: GPU Device Information
The system SHALL provide information about the GPU device being used.

#### Scenario: GPU name reporting
- **WHEN** the system starts or status is queried
- **THEN** the system SHALL report the GPU device name (e.g., "GeForce GTX 1050 Ti")

#### Scenario: CUDA version reporting
- **WHEN** the system starts or status is queried
- **THEN** the system SHALL report the CUDA version being used

#### Scenario: Compute capability reporting
- **WHEN** the system starts or status is queried
- **THEN** the system SHALL report the GPU compute capability (e.g., "6.1")

### Requirement: Memory Leak Detection
The system SHALL detect and report potential memory leaks.

#### Scenario: Baseline memory tracking
- **WHEN** the system starts with no models loaded
- **THEN** the system SHALL record the baseline VRAM usage

#### Scenario: Memory leak detection
- **WHEN** VRAM usage increases beyond expected levels after multiple operations
- **THEN** the system SHALL log a warning about potential memory leaks

#### Scenario: Memory leak threshold
- **WHEN** VRAM usage exceeds baseline by more than 500MB without a loaded model
- **THEN** the system SHALL trigger a memory leak alert

### Requirement: Logging and Diagnostics
The system SHALL log GPU-related events for debugging and monitoring.

#### Scenario: Model load logging
- **WHEN** a model is loaded
- **THEN** the system SHALL log the model name, load time, and resulting VRAM usage

#### Scenario: Model unload logging
- **WHEN** a model is unloaded
- **THEN** the system SHALL log the model name, unload time, and freed VRAM

#### Scenario: VRAM threshold warnings
- **WHEN** VRAM usage exceeds 90% of available memory
- **THEN** the system SHALL log a warning message

#### Scenario: GPU error logging
- **WHEN** a CUDA error occurs
- **THEN** the system SHALL log the error details including error code and message

### Requirement: Performance Degradation Alerts
The system SHALL alert when performance degrades below acceptable thresholds.

#### Scenario: Slow model switch alert
- **WHEN** a model switch takes longer than 20 seconds
- **THEN** the system SHALL log a performance degradation warning

#### Scenario: High memory pressure alert
- **WHEN** VRAM usage remains above 85% for more than 5 minutes
- **THEN** the system SHALL log a memory pressure warning

#### Scenario: Frequent switching alert
- **WHEN** model switches occur more than 10 times per minute
- **THEN** the system SHALL log a warning about excessive switching
