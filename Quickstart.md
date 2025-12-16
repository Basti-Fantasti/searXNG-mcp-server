# Quickstart Guide

Get up and running with the SearXNG MCP Server in under 10 minutes! This guide walks you through everything you need to enable privacy-focused web search in Claude Desktop and Claude Code.

## What You'll Build

By the end of this guide, you'll have:
- ✅ A local SearXNG search engine running in Docker
- ✅ The SearXNG MCP server installed and configured
- ✅ Claude Desktop/Claude Code connected to your private search engine
- ✅ The ability to perform web searches without tracking or ads

## Prerequisites

Before starting, install these required tools:

### 1. Python 3.13 or Higher

**Check if you have Python:**
```bash
python --version
```

**If you need to install Python:**
- Download from [python.org/downloads](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Restart your terminal after installation

### 2. uv (Python Package Manager)

**Install uv:**

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 3. Docker

Docker runs the SearXNG search engine in a container.

**Install Docker:**
- **Windows/macOS**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/)

**Verify Docker is running:**
```bash
docker --version
docker ps
```

If `docker ps` works without errors, you're ready!

---

## Step 1: Get the Code

Clone the repository and navigate into it:

```bash
git clone <YOUR_REPO_URL>.git
cd searxng-mcp-server
```

**Don't have git?**
- Download the ZIP file from GitHub
- Extract it
- Open terminal/command prompt in the extracted folder

---

## Step 2: Start SearXNG Search Engine

SearXNG is the privacy-focused search engine that powers this MCP server. Let's get it running!

### Start the Container

```bash
docker-compose up -d
```

**What this does:**
- Downloads the SearXNG Docker image (first time only)
- Starts SearXNG on `http://localhost:9999`
- Runs in the background (`-d` = detached mode)

### Verify SearXNG is Working

**Check the container is running:**
```bash
docker ps
```

You should see a container named `searxng-searxng-1` or similar.

**Test the search API:**
```bash
# macOS/Linux
curl "http://localhost:9999/search?q=test&format=json"

# Windows (PowerShell)
Invoke-WebRequest "http://localhost:9999/search?q=test&format=json"
```

You should see JSON output with search results. If you get a connection error, wait 10-20 seconds for SearXNG to fully start, then try again.

**View the web interface (optional):**

Open your browser to [http://localhost:9999](http://localhost:9999) to see the SearXNG search interface.

---

## Step 3: Install the MCP Server

Now let's install the MCP server that connects Claude to SearXNG.

### Install Dependencies

```bash
uv sync
```

**What this does:**
- Creates a virtual environment in `.venv/`
- Installs all required Python packages (mcp, httpx, pydantic, etc.)

This takes 30-60 seconds on the first run.

### Test the Installation

```bash
uv run searxng-mcp --help
```

If this shows help output or doesn't error, the installation succeeded!

---

## Step 4: Configure Claude Desktop

Now we'll connect Claude Desktop to your MCP server.

### Find Your Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
```
Look for `claude_desktop_config.json`

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**If the file doesn't exist:** Create it in that location.

### Add the MCP Server Configuration

Copy and paste this into `claude_desktop_config.json`:

**macOS/Linux:**
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

**Windows:**
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

### ⚠️ IMPORTANT: Replace the Path

**Find your absolute path:**

```bash
# macOS/Linux
pwd

# Windows (PowerShell)
Get-Location
```

Copy the output and replace `/absolute/path/to/searxng-mcp-server` with your actual path.

**Example paths:**
- macOS: `/Users/john/projects/searxng-mcp-server`
- Linux: `/home/john/projects/searxng-mcp-server`
- Windows: `C:\\Users\\john\\projects\\searxng-mcp-server`

**Windows users:** Use double backslashes `\\` or forward slashes `/`

### Restart Claude Desktop

**Completely quit and restart Claude Desktop** for the changes to take effect.

- **macOS**: Cmd+Q then reopen
- **Windows**: Right-click taskbar icon → Quit, then reopen
- **Linux**: Close all windows and reopen

---

## Step 5: Test Your Setup

### In Claude Desktop

Start a new conversation and try:

```
Can you search for "Python async programming" and summarize the top results?
```

Claude should use the `web_search` tool to query your local SearXNG instance and return results!

**You should see:**
- A "Using web_search" indicator
- Search results from various sources
- No tracking or ads (it's your private instance!)

---

## Step 6: Claude Code Setup (Optional)

If you use Claude Code (the CLI tool), it will automatically detect the MCP server configured in Claude Desktop. No additional setup needed!

Alternatively, you can configure it separately within Claude Code's MCP settings.

---

## Example Queries to Try

Now that everything is set up, try these example queries:

### Basic Search
```
Search for "best practices for REST API design"
```

### Get Recent News
```
Find news articles about renewable energy from the past week
```

### Multiple Results
```
Search for "machine learning tutorials" and give me 20 results
```

### Category-Specific Search
```
Search for "quantum computing" in science and news categories only
```

Available categories: `general`, `news`, `images`, `videos`, `files`, `science`, `map`, `music`, `it`

### Language-Specific Search
```
Search for "recettes de cuisine" in French
```

Common language codes: `en` (English), `de` (German), `fr` (French), `es` (Spanish), `it` (Italian), `pt` (Portuguese), `ru` (Russian), `zh` (Chinese), `ja` (Japanese)

### Time-Filtered Search
```
Search for "AI breakthroughs" from the past month
```

Time ranges: `day`, `week`, `month`, `year`

### Advanced Combined Search
```
Search for "climate change research" in English, in science category, from the past year, limit to 15 results
```

---

## Troubleshooting

### Problem: "Failed to connect to SearXNG"

**Possible causes:**
1. SearXNG isn't running
2. Wrong port in configuration
3. Docker isn't running

**Solutions:**

**Check if SearXNG is running:**
```bash
docker ps | grep searxng
```

**If not running, start it:**
```bash
docker-compose up -d
```

**Test the connection manually:**
```bash
curl "http://localhost:9999/search?q=test&format=json"
```

**Check Docker is running:**
```bash
docker info
```

If Docker isn't running, start Docker Desktop.

---

### Problem: "Claude Desktop doesn't show the MCP server"

**Possible causes:**
1. Relative path used instead of absolute path
2. Path doesn't exist
3. Claude Desktop wasn't restarted

**Solutions:**

**Verify your path is absolute:**
- ❌ Wrong: `./searxng-mcp-server` (relative)
- ✅ Correct: `/Users/john/projects/searxng-mcp-server` (absolute)

**Check the path exists:**
```bash
# macOS/Linux
ls /your/absolute/path/to/searxng-mcp-server

# Windows
dir X:\your\absolute\path\to\searxng-mcp-server
```

**Completely restart Claude Desktop:**
- Quit the app entirely (not just close windows)
- Wait 5 seconds
- Reopen it

**Check Claude Desktop logs:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`
- Look for errors mentioning "searxng"

---

### Problem: "Search requests are timing out"

**Possible causes:**
1. SearXNG is slow or overloaded
2. Network issues
3. Timeout is too short

**Solutions:**

**Check SearXNG logs:**
```bash
docker logs searxng
```

**Restart SearXNG:**
```bash
docker-compose restart
```

**Increase timeout (create `.env` file):**
```bash
# Create .env in the project directory
SEARXNG_BASE_URL=http://localhost:9999
SEARXNG_TIMEOUT=30
LOG_LEVEL=INFO
```

Then restart Claude Desktop.

---

### Problem: "Permission denied" (Windows)

**Possible causes:**
1. Insufficient permissions
2. Antivirus blocking uv or Python
3. File permissions issue

**Solutions:**

**Run terminal as Administrator:**
- Right-click Command Prompt or PowerShell
- Select "Run as Administrator"

**Check antivirus:**
- Temporarily disable antivirus
- Try running the command again
- If it works, add an exception for uv and Python

**Check file permissions:**
- Right-click project folder → Properties → Security
- Ensure your user has full control

---

### Problem: "No search results returned"

**Possible causes:**
1. SearXNG search engines not configured
2. Network issues in container
3. Invalid query parameters

**Solutions:**

**Test SearXNG directly:**
```bash
curl "http://localhost:9999/search?q=test&format=json"
```

**Check if you get results in browser:**
- Open [http://localhost:9999](http://localhost:9999)
- Try a search manually

**Check SearXNG configuration:**
```bash
docker logs searxng | grep -i error
```

**Try a simpler query:**
- Remove filters (categories, time ranges, language)
- Use a basic query like "test" or "python"

---

### Problem: "Module not found" or "Import errors"

**Possible causes:**
1. Dependencies not installed
2. Wrong Python version
3. Virtual environment not activated

**Solutions:**

**Reinstall dependencies:**
```bash
uv sync --reinstall
```

**Check Python version:**
```bash
python --version
```

Must be 3.13 or higher.

**Verify uv is working:**
```bash
uv --version
```

**Try running with explicit uv:**
```bash
uv run python -c "import searxng_mcp; print('Success!')"
```

---

## Next Steps

Now that you're up and running:

1. **Explore the Features**: Try different search parameters (categories, languages, time ranges)
2. **Read the Full README**: Check out [README.md](README.md) for advanced configuration options
3. **Customize SearXNG**: Edit `searxng-settings.yml` to configure search engines and preferences
4. **Contribute**: Found a bug or want to add a feature? See our [Contributing Guide](README.md#contributing)

---

## Daily Usage

### Starting Your Day

```bash
# Start SearXNG
docker-compose up -d

# Open Claude Desktop
# Start searching!
```

### Stopping Everything

```bash
# Stop SearXNG (optional, only if you want to free up resources)
docker-compose down
```

**Note:** You can leave SearXNG running in the background. It uses minimal resources and starts automatically with Docker Desktop.

---

## Advanced Configuration (Optional)

### Custom Environment Variables

Create a `.env` file in the project directory:

```bash
# .env
SEARXNG_BASE_URL=http://localhost:9999
SEARXNG_TIMEOUT=10
LOG_LEVEL=INFO
MAX_RESULTS_LIMIT=50
```

**Available options:**

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARXNG_BASE_URL` | URL of your SearXNG instance | `http://localhost:8080`<br>(Use `9999` with docker-compose) |
| `SEARXNG_TIMEOUT` | Request timeout in seconds | `10` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `MAX_RESULTS_LIMIT` | Maximum results per query | `50` |

### Different SearXNG Port

If port 9999 is already in use, edit `docker-compose.yaml`:

```yaml
services:
  searxng:
    ports:
      - "8888:8080"  # Change 9999 to your preferred port
```

Then update your `.env` and Claude Desktop config to match.

---

## Getting Help

**Need assistance?**

- **Issues**: [GitHub Issues](<YOUR_REPO_URL>/issues)
- **Discussions**: [GitHub Discussions](<YOUR_REPO_URL>/discussions)
- **SearXNG Docs**: [docs.searxng.org](https://docs.searxng.org)
- **MCP Docs**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

**Happy searching! 🔍 Your searches are now private and ad-free.**
