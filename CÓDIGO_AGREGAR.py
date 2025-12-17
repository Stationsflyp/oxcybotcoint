"""
INSTRUCCIONES DE INTEGRACIÓN
=============================

Abre el archivo "OxcyShop - Store Management.py"
y agrega ESTE código en el método on_ready() DESPUÉS de la línea:
    bot.loop.create_task(change_status())

NO necesitas modificar nada más. Solo pega este código.
"""

# ════════════════════════════════════════════════════════════════════════════
# AGREGAR ESTO EN EL MÉTODO on_ready() (después de bot.loop.create_task)
# ════════════════════════════════════════════════════════════════════════════

    # --- CARGAR MÓDULOS DE IDENTITY BAN ---
    try:
        await bot.load_extension("modules.identity_ban.events")
        print("✅ Módulo de eventos Identity Ban cargado")
    except Exception as e:
        print(f"❌ Error cargando módulo events: {e}")
    
    try:
        await bot.load_extension("modules.identity_ban.commands")
        print("✅ Módulo de comandos Identity Ban cargado")
    except Exception as e:
        print(f"❌ Error cargando módulo commands: {e}")


# ════════════════════════════════════════════════════════════════════════════
# CÓDIGO EXACTO DEL MÉTODO on_ready() COMPLETO
# ════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    bot.loop.create_task(change_status())
    
    # --- CARGAR MÓDULOS DE IDENTITY BAN ---
    try:
        await bot.load_extension("modules.identity_ban.events")
        print("✅ Módulo de eventos Identity Ban cargado")
    except Exception as e:
        print(f"❌ Error cargando módulo events: {e}")
    
    try:
        await bot.load_extension("modules.identity_ban.commands")
        print("✅ Módulo de comandos Identity Ban cargado")
    except Exception as e:
        print(f"❌ Error cargando módulo commands: {e}")
    
    service_channel = bot.get_channel(SERVICE_CHANNEL_ID)
    if service_channel:
        embed = discord.Embed(
            title="🎨 OxcyShop Store",
            description="Click the button below to start your order. Fill in your UI and payment details in the form.",
            color=0xFF0000
        )
        embed.set_footer(text="OxcyShop - UI Design Marketplace")
        view = StartBuyingView()
        await service_channel.send(embed=embed, view=view)


# ════════════════════════════════════════════════════════════════════════════
# PERMISOS REQUERIDOS EN DISCORD
# ════════════════════════════════════════════════════════════════════════════

"""
Asegúrate de que tu bot tiene estos permisos:
✅ Ver canales
✅ Enviar mensajes
✅ Leer historial de mensajes
✅ Usar comandos de aplicación
✅ Administrar servidores (para detectar banes)
"""


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE IDS
# ════════════════════════════════════════════════════════════════════════════

"""
Si quieres cambiar los canales de alertas, abre:
    modules/identity_ban/events.py

Y modifica estas líneas:
    ALERT_CHANNEL_ID = 1448647845921161267       # Canal de alertas
    DATA_CHANNEL_ID = 1448647859363905619        # Canal de datos de banes
"""


# ════════════════════════════════════════════════════════════════════════════
# COMANDOS DISPONIBLES
# ════════════════════════════════════════════════════════════════════════════

"""
Después de integrar, los siguientes comandos estarán disponibles:

1. /check_trust @usuario
   → Verifica el Trust Score de un usuario

2. /view_bans
   → Muestra todos los banes registrados

3. /search_user <ID>
   → Busca un usuario en los registros

Los comandos se usan en Discord escribiendo:
    /check_trust @nombre
    /view_bans
    /search_user 123456789
"""


# ════════════════════════════════════════════════════════════════════════════
# ESTRUCTURA ESPERADA
# ════════════════════════════════════════════════════════════════════════════

"""
Después de completar la integración, tendrás:

OxcyShop_Store/
├── OxcyShop - Store Management.py
├── oxcywebhook.py
├── requirements.txt
├── identity_data.txt  ← NUEVA BASE DE DATOS EN TEXTO
├── modules/
│   └── identity_ban/
│       ├── __init__.py
│       ├── identity_manager.py
│       ├── trust_score.py
│       ├── events.py
│       └── commands.py
└── INTEGRACIÓN_IDENTITY_BAN.md
"""
