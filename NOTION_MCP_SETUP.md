# Notion MCP Setup Instructions

Pasos que Pablo seguirá:
Abrir el repo en Codex  
Descarga o clona este repositorio en su entorno y ábrelo en Codex.
Configurar el MCP de Notion  
Si la configuración ya viene en el repo, no necesitas crear nada adicional.  

Si no está configurado, crea el archivo ~/.codex/config.toml con este contenido:

[mcp_servers.notion]
url = "https://mcp.notion.com/mcp"
​
Reiniciar Codex  
Cierra y vuelve a abrir Codex/VS Code para que cargue la configuración del MCP.
Autenticarse con la cuenta de Notion de Pablo (primera vez)  
Al primer uso del MCP, Codex abrirá un navegador para iniciar sesión en Notion y autorizar el acceso con la cuenta de Pablo.

Test rápido (verificar que el MCP está funcionando)  
En Codex, ejecutar una acción de prueba (solo lectura), por ejemplo:  

“List MCP tools from server notion (listTools)”, o  
“Search a Notion page using the notion MCP server”.
Ejecutar el skill  

Una vez autenticado, el skill podrá operar en Notion con los permisos de la cuenta con la que Pablo autorizó (lectura/escritura según los permisos concedidos).

ADVERTENCIA OFICIAL (documentación):  
“Notion MCP requiere OAuth de usuario y NO soporta tokens. Esto puede no ser adecuado para agentes en la nube que corren sin interacción humana.”
