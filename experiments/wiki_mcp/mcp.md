## Building an MCP server

https://github.com/modelcontextprotocol/python-sdk

MCP servers provide the following capabilities:
https://modelcontextprotocol.io/specification/2025-06-18/server
1. Resources
2. Tools
3. Prompts

2 types of transports:
1. stdio
2. streamable http - can support multiple client connections for each server instance
- it's possible I only need one client per server.

- it appears that `run --with mcp[cli] mcp run C:\Users\Jonathan\Documents\CODE\riothack\experiments\mcp\server.py` is run when Claude Desktop app is opened

(official) https://wiki.leagueoflegends.com/en-us/
(unofficial)  https://leagueoflegends.fandom.com/wiki/League_of_Legends_Wiki