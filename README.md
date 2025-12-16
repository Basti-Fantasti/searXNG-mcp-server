# SearXNG MCP Server

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

A Model Context Protocol (MCP) server that provides privacy-focused web search capabilities through [SearXNG](https://github.com/searxng/searxng), a free metasearch engine. This server enables Claude Desktop and Claude Code to perform web searches while maintaining user privacy.

## Features

- **Privacy-Focused Search**: Leverages SearXNG for anonymous, tracker-free web searches
- **Advanced Search Parameters**: Support for categories, language filters, and time ranges
- **MCP Integration**: Seamlessly integrates with Claude Desktop and Claude Code
- **Async Architecture**: Built with async/await for non-blocking, efficient operations
- **Type Safety**: Full type hints and Pydantic models for robust data validation
- **Configurable**: Environment-based configuration for flexible deployment
- **Local SearXNG Instance**: Uses Docker to run SearXNG locally for complete privacy control

## Prerequisites

Before installing, ensure you have:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **uv** - Fast Python package installer and resolver
  ```bash
  # Install uv (macOS/Linux)
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Install uv (Windows)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Docker** - Required for running SearXNG locally
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS)
  - [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

## Installation

### 1. Clone the Repository

```bash
git clone <YOUR_REPO_URL>.git
cd searxng-mcp-server
```

### 2. Install Dependencies

```bash
# Install dependencies using uv
uv sync

# This will create a virtual environment and install all required packages
```

### 3. Configure Environment (Optional)

Create a `.env` file to customize configuration:

```bash
# .env
SEARXNG_BASE_URL=http://localhost:9999
SEARXNG_TIMEOUT=10
LOG_LEVEL=INFO
MAX_RESULTS_LIMIT=50
```

**Configuration Options:**

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARXNG_BASE_URL` | Base URL of your SearXNG instance | `http://localhost:8080`<br>(Use `9999` with docker-compose) |
| `SEARXNG_TIMEOUT` | Request timeout in seconds | `10` |
| `LOG_LEVEL` | Logging verbosity (DEBUG/INFO/WARNING/ERROR/CRITICAL) | `INFO` |
| `MAX_RESULTS_LIMIT` | Maximum results allowed per query | `50` |

## SearXNG Docker Setup

The server requires a running SearXNG instance. Use Docker Compose for easy setup:

### 1. Start SearXNG

```bash
# Start SearXNG container in detached mode
docker-compose up -d
```

This will:
- Pull the official SearXNG Docker image
- Start SearXNG on port 9999 (mapped from container port 8080)
- Mount the `searxng-settings.yml` configuration file

### 2. Verify SearXNG is Running

```bash
# Check container status
docker ps | grep searxng

# Test SearXNG API
curl "http://localhost:9999/search?q=test&format=json"
```

### 3. Stop SearXNG

```bash
# Stop the container
docker-compose down
```

### 4. View Logs

```bash
# View SearXNG logs
docker logs searxng

# Follow logs in real-time
docker logs -f searxng
```

## Claude Desktop Configuration

To use this MCP server with Claude Desktop, add it to your configuration file:

### macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "searxng": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/searxng-mcp-server",
        "run",
        "searxng-mcp"
      ],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:9999"
      }
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "searxng": {
      "command": "uv",
      "args": [
        "--directory",
        "X:\\absolute\\path\\to\\searxng-mcp-server",
        "run",
        "searxng-mcp"
      ],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:9999"
      }
    }
  }
}
```

**Important Notes:**
- Use **absolute paths**, not relative paths
- Restart Claude Desktop after modifying the configuration
- Ensure SearXNG is running before starting Claude Desktop

## Claude Code Configuration

Claude Code automatically detects and uses MCP servers configured in Claude Desktop. No additional configuration needed.

Alternatively, you can configure it separately in the MCP settings within Claude Code.

## Usage Examples

Once configured, you can use the `web_search` tool in Claude Desktop or Claude Code:

### Basic Search

```
Search for "Python async programming tutorials"
```

### Search with Maximum Results

```
Search for "machine learning news" and return up to 20 results
```

### Category-Specific Search

```
Search for "climate change" in the science and news categories
```

Available categories:
- `general` - General web search
- `news` - News articles
- `images` - Image search
- `videos` - Video content
- `files` - File downloads
- `science` - Scientific papers and resources
- `map` - Maps and locations
- `music` - Music content
- `it` - IT and tech resources

### Language-Specific Search

```
Search for "recettes françaises" in French
```

Use ISO 639-1 language codes: `en`, `de`, `fr`, `es`, `it`, `pt`, `ru`, `zh`, `ja`, etc.

### Time-Range Filtered Search

```
Search for "AI breakthroughs" from the past week
```

Available time ranges:
- `day` - Past 24 hours
- `week` - Past 7 days
- `month` - Past 30 days
- `year` - Past year

### Combined Advanced Search

```
Search for "renewable energy" in English, in science and news categories, from the past month, limit to 15 results
```

## Troubleshooting

### SearXNG Connection Issues

**Problem:** `Failed to connect to SearXNG`

**Solutions:**
- Verify SearXNG is running: `docker ps | grep searxng`
- Check the URL is correct: `curl http://localhost:9999/search?q=test&format=json`
- Ensure the port (9999) matches your `docker-compose.yaml` and configuration
- Check Docker is running: `docker info`

### Timeout Errors

**Problem:** `Search request timed out`

**Solutions:**
- Increase timeout in `.env`: `SEARXNG_TIMEOUT=30`
- Check SearXNG performance: `docker logs searxng`
- Restart SearXNG container: `docker-compose restart`

### Claude Desktop Not Finding the Server

**Problem:** MCP server not showing up in Claude Desktop

**Solutions:**
- Verify you're using **absolute paths** in the configuration
- Check the path exists: `ls /absolute/path/to/searxng-mcp-server`
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

### Permission Errors on Windows

**Problem:** `Permission denied` when running uv or accessing files

**Solutions:**
- Run terminal as Administrator
- Check file permissions in the project directory
- Ensure your antivirus isn't blocking uv or Python

### No Search Results Returned

**Problem:** Search returns empty results

**Solutions:**
- Test SearXNG directly: `curl "http://localhost:9999/search?q=test&format=json"`
- Check SearXNG settings in `searxng-settings.yml`
- Verify search engines are enabled in SearXNG
- Try a different query or remove filters

## Development Setup

### Install Development Dependencies

```bash
# Install dev dependencies
uv sync --dev
```

This installs additional tools:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checker
- `ruff` - Fast Python linter and formatter

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/searxng_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run with verbose output
uv run pytest -v

# Run async tests
uv run pytest -v tests/test_searxng_client.py
```

Coverage reports are generated in `htmlcov/index.html`.

### Code Quality Checks

```bash
# Run linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy src/searxng_mcp
```

### Running the Server Locally

```bash
# Run the MCP server
uv run searxng-mcp
```

The server uses stdio transport and expects MCP protocol messages on stdin.

### Project Structure

```
searxng-mcp-server/
├── src/
│   └── searxng_mcp/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point
│       ├── server.py           # MCP server implementation
│       ├── searxng_client.py   # SearXNG HTTP client
│       ├── config.py           # Configuration management
│       └── models.py           # Pydantic data models
├── tests/
│   ├── test_server.py          # Server tests
│   ├── test_searxng_client.py  # Client tests
│   └── test_config.py          # Config tests
├── docker-compose.yaml         # SearXNG container config
├── searxng-settings.yml        # SearXNG configuration
├── pyproject.toml              # Project metadata and dependencies
├── CLAUDE.md                   # Claude Code project guide
└── README.md                   # This file
```

## Contributing

Contributions are welcome! Here's how to contribute:

### 1. Fork and Clone

```bash
git clone <YOUR_REPO_URL>.git
cd searxng-mcp-server
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow existing code style (enforced by Ruff)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass: `uv run pytest`
- Run linting: `uv run ruff check .`
- Run type checking: `uv run mypy src/searxng_mcp`

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add your descriptive commit message"
```

Use conventional commit messages:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reference any related issues
- Screenshots/examples if applicable

### Code Review Process

- All PRs require passing tests
- Code must pass linting and type checking
- At least one maintainer approval required
- Documentation must be updated for user-facing changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SearXNG](https://github.com/searxng/searxng) - The privacy-respecting metasearch engine
- [Model Context Protocol](https://modelcontextprotocol.io) - The protocol enabling AI tool integration
- [Anthropic](https://www.anthropic.com) - For Claude and the MCP SDK

## Support

- **Issues**: [GitHub Issues](<YOUR_REPO_URL>/issues)
- **Discussions**: [GitHub Discussions](<YOUR_REPO_URL>/discussions)
- **SearXNG Documentation**: [docs.searxng.org](https://docs.searxng.org)
- **MCP Documentation**: [modelcontextprotocol.io/docs](https://modelcontextprotocol.io/docs)

---

**Built with privacy in mind. Search freely.**
