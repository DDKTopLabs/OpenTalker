## ADDED Requirements

### Requirement: PyPI Mirror Configuration
The system SHALL configure uv to use Tsinghua University PyPI mirror as the default package index.

#### Scenario: Default PyPI mirror
- **WHEN** the system installs Python packages
- **THEN** the system SHALL use https://pypi.tuna.tsinghua.edu.cn/simple as the primary index

#### Scenario: Fallback to official PyPI
- **WHEN** a package is not available on the Tsinghua mirror
- **THEN** the system SHALL automatically fall back to the official PyPI

#### Scenario: Mirror configuration in pyproject.toml
- **WHEN** the project is configured
- **THEN** the pyproject.toml SHALL contain `[[tool.uv.index]]` entries for both Tsinghua and official PyPI

### Requirement: PyTorch Mirror Configuration
The system SHALL configure uv to use Tsinghua University PyTorch mirror for PyTorch packages.

#### Scenario: PyTorch package pinning
- **WHEN** the system installs torch or torchaudio
- **THEN** the system SHALL use the Tsinghua PyTorch mirror via `tool.uv.sources` configuration

#### Scenario: Explicit index for PyTorch
- **WHEN** PyTorch packages are installed
- **THEN** the system SHALL use https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu121 as an explicit index

#### Scenario: CUDA version matching
- **WHEN** PyTorch is installed
- **THEN** the system SHALL use the cu121 (CUDA 12.1) wheel variant

#### Scenario: Prevent dependency confusion
- **WHEN** the PyTorch index is configured
- **THEN** the system SHALL mark it as `explicit = true` to prevent non-PyTorch packages from using this index

### Requirement: HuggingFace Mirror Configuration
The system SHALL configure HuggingFace Hub to use HF-Mirror for model downloads.

#### Scenario: HF_ENDPOINT environment variable
- **WHEN** the system downloads models from HuggingFace
- **THEN** the system SHALL use HF_ENDPOINT=https://hf-mirror.com

#### Scenario: Model cache location
- **WHEN** models are downloaded
- **THEN** the system SHALL cache them in the directory specified by HUGGINGFACE_HUB_CACHE

#### Scenario: Automatic mirror usage
- **WHEN** qwen-asr or other HuggingFace-based packages download models
- **THEN** the downloads SHALL automatically use the HF-Mirror endpoint

### Requirement: Docker Mirror Configuration
The system SHALL configure Docker to use Tsinghua University Docker mirror for faster image pulls.

#### Scenario: Docker daemon configuration
- **WHEN** Docker is configured
- **THEN** the daemon.json SHALL include https://docker.mirrors.tuna.tsinghua.edu.cn as a registry mirror

#### Scenario: Base image pull acceleration
- **WHEN** the Dockerfile builds the NVIDIA CUDA base image
- **THEN** the image SHALL be pulled through the configured mirror

#### Scenario: Multiple mirror fallback
- **WHEN** the primary Docker mirror fails
- **THEN** the system SHALL fall back to alternative mirrors or the official registry

### Requirement: Ubuntu APT Mirror Configuration
The system SHALL configure Ubuntu APT to use Tsinghua University mirror for system packages.

#### Scenario: APT sources replacement
- **WHEN** the Dockerfile installs system packages
- **THEN** the system SHALL replace archive.ubuntu.com with mirrors.tuna.tsinghua.edu.cn in sources.list

#### Scenario: Security updates mirror
- **WHEN** security updates are installed
- **THEN** the system SHALL use the Tsinghua mirror for security.ubuntu.com as well

#### Scenario: Package installation acceleration
- **WHEN** apt-get install is executed
- **THEN** the packages SHALL be downloaded from the Tsinghua mirror

### Requirement: Mirror Configuration Validation
The system SHALL validate that mirror configurations are working correctly.

#### Scenario: PyPI mirror connectivity test
- **WHEN** the system starts or during health checks
- **THEN** the system SHALL verify connectivity to the Tsinghua PyPI mirror

#### Scenario: PyTorch mirror connectivity test
- **WHEN** PyTorch packages need to be installed
- **THEN** the system SHALL verify the PyTorch mirror is accessible

#### Scenario: HF mirror connectivity test
- **WHEN** models need to be downloaded
- **THEN** the system SHALL verify the HF-Mirror endpoint is accessible

#### Scenario: Fallback on mirror failure
- **WHEN** a mirror is unreachable
- **THEN** the system SHALL automatically fall back to official sources and log a warning

### Requirement: Mirror Configuration Documentation
The system SHALL provide clear documentation for mirror configuration.

#### Scenario: Configuration file comments
- **WHEN** users view pyproject.toml
- **THEN** the file SHALL include comments explaining the mirror configuration

#### Scenario: Environment variable documentation
- **WHEN** users view .env.example
- **THEN** the file SHALL document all mirror-related environment variables

#### Scenario: README instructions
- **WHEN** users read the README
- **THEN** the documentation SHALL explain how to switch between mirrors and official sources

### Requirement: Regional Configuration Flexibility
The system SHALL allow users to easily switch between Chinese mirrors and official sources.

#### Scenario: Disable mirrors via environment variable
- **WHEN** a user sets USE_CHINA_MIRRORS=false
- **THEN** the system SHALL use official sources instead of Chinese mirrors

#### Scenario: Mirror URL customization
- **WHEN** a user specifies custom mirror URLs in environment variables
- **THEN** the system SHALL use the custom URLs instead of defaults

#### Scenario: Automatic region detection
- **WHEN** the system starts without explicit mirror configuration
- **THEN** the system SHALL use Chinese mirrors by default (as this is the target deployment region)
