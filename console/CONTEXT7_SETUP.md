# Context 7 MCP Setup

Context 7 is an MCP (Model Context Protocol) server that provides up-to-date code documentation for AI code editors and language models.

## Installation

Context 7 has been installed as a dependency:

```bash
pnpm add @upstash/context7-mcp
```

## Configuration for MCP Clients

### For Cursor

Add to your Cursor configuration file:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

### For VS Code with Continue

Add to your Continue configuration:

```json
{
  "mcpServers": [
    {
      "name": "context7",
      "url": "https://mcp.context7.com/mcp"
    }
  ]
}
```

### For Claude Desktop (macOS)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

## Usage

When using your AI code editor, simply add "use context7" to your prompts to get version-specific, up-to-date code examples.

Example prompts:

- "use context7: show me how to implement auth with NextAuth.js in Next.js 15"
- "use context7: what's the latest way to handle server actions in Next.js?"
- "use context7: show me the current best practices for React Server Components"

## Running Locally

To run the Context 7 MCP server locally:

```bash
npx -y @upstash/context7-mcp@latest
```

This will start the MCP server on stdio, ready to be used by your MCP client.
