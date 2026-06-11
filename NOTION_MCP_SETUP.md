# Notion MCP Setup Instructions

Pasos exactos que Pablo seguira:
1. Abrir tu repo en Codex
Descarga o clona tu repositorio en su entorno.

2. Agregar la configuracion del MCP
Si no esta en el repo, crea ~/.codex/config.toml con:

[mcp_servers.notion]
url = "https://mcp.notion.com/mcp"

3. Autenticarse con SU cuenta de Notion
codex mcp login notion
Se abre un navegador → inicia sesion con su cuenta gratuita de Notion → autoriza el acceso.

4. Ejecutar tu skill
El agente ya puede publicar reportes en el workspace de Notion de Pablo.

ADVERTENCIA OFICIAL de la documentacion
"Notion MCP requiere OAuth de usuario y NO soporta tokens. Esto puede no ser adecuado para agentes en la nube que corren sin interaccion humana."
