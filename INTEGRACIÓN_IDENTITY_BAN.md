# 🔐 Sistema Ban Trust Score - Guía de Integración

## 📋 Descripción General

Sistema completo de "Ban por Identidad" (Ban Trust Score) que identifica alts, ban evaders y usuarios sospechosos al unirse al servidor, SIN usar base de datos - todo guardado en un único archivo de texto.

## 📁 Estructura de Carpetas

```
OxcyShop_Store/
├── OxcyShop - Store Management.py (tu bot principal)
├── modules/
│   └── identity_ban/
│       ├── __init__.py
│       ├── identity_manager.py    (Lectura/escritura del .txt)
│       ├── trust_score.py         (Cálculo del Trust Score)
│       ├── events.py              (Eventos del bot)
│       └── commands.py            (Comandos slash)
├── identity_data.txt              (Base de datos de banes en texto)
└── INTEGRACIÓN_IDENTITY_BAN.md    (Este archivo)
```

## 🔧 Integración en tu Bot

### Paso 1: Modificar tu bot principal

Abre **`OxcyShop - Store Management.py`** y agrega estas líneas ANTES de `bot.run(TOKEN)`:

```python
# --- CARGAR MÓDULOS DE BAN IDENTITY ---
import os
from modules.identity_ban import events, commands as identity_commands

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    
    # Cargar módulos de Identity Ban
    await bot.load_extension("modules.identity_ban.events")
    await bot.load_extension("modules.identity_ban.commands")
    
    bot.loop.create_task(change_status())
    # ... resto del código de on_ready
```

### Paso 2: Verificar configuración de intents

Asegúrate de que tu bot tiene los intents correctos (ya lo tienes):

```python
intents = discord.Intents.default()
intents.members = True          # ✅ Necesario para on_member_join
intents.message_content = True  # ✅ Ya está
intents.guilds = True           # ✅ Necesario para bans
```

### Paso 3: Configurar IDs de Canales

En **`modules/identity_ban/events.py`**, actualiza estos IDs:

```python
ALERT_CHANNEL_ID = 1448647845921161267       # Canal donde se envían alertas
DATA_CHANNEL_ID = 1448647859363905619        # Canal donde se guardan datos de banes
```

## 🎯 Funcionalidades

### 1. **Registro Automático de Banes** 📌
- Cuando un usuario es baneado, se registra automáticamente en `identity_data.txt`
- Se envía un embed con toda la información al canal de datos
- Incluye: ID, usuario, fecha, servidor, razón, historial

### 2. **Análisis de Nuevos Miembros** 👁️
- Cuando alguien se une, el bot calcula automáticamente su Trust Score
- Si es sospechoso (puntuación < 70), envía alerta al canal de alertas
- Incluye detalles de por qué fue marcado como sospechoso

### 3. **Trust Score (0-100 puntos)** 📊

**Desglose:**
- **Antigüedad de cuenta** (0-25 puntos): Cuentas más viejas = más puntos
  - > 2 años: 25 puntos
  - > 1 año: 20 puntos
  - > 6 meses: 15 puntos
  - > 3 meses: 10 puntos
  - > 1 mes: 5 puntos
  - Menos: 0 puntos

- **Similaridad de nombre** (0-20 puntos): Detecta nombres similares a baneados
  - > 85% similar: -20 puntos (10-20 rango final)
  - > 70% similar: -10 puntos
  - > 50% similar: -5 puntos

- **Similaridad de avatar** (0-15 puntos): Detecta avatares duplicados
  - Avatar idéntico: 0 puntos

- **Overlap de servidor** (0-15 puntos): Si comparte servidor con baneados
  - Comparte servidor: -10 puntos

- **Patrón de ID** (0-10 puntos): Detecta IDs secuenciales sospechosas
  - Diferencia < 100: -10 puntos
  - Diferencia < 1000: -5 puntos

### 4. **Recomendaciones Automáticas** 💡
- **Score < 50**: 🔴 BAN RECOMENDADO
- **Score 50-70**: 🟠 KICK RECOMENDADO
- **Score 70-85**: 🟡 MONITOREAR
- **Score > 85**: ✅ SIN SOSPECHAS

## 📖 Comandos Disponibles

### `/check_trust @usuario`
Verifica el Trust Score de un usuario específico

**Respuesta:**
```
🔍 ANÁLISIS DE TRUST SCORE
👤 Usuario: NombreUsuario#1234
🆔 ID: 123456789
📅 Cuenta Creada: 2023-06-15
🎯 Trust Score: 🟢 87/100

📊 Desglose Detallado:
✓ Antigüedad de cuenta: 25/25
✓ Similaridad de nombre: 20/20
✓ Similaridad de avatar: 15/15
✓ Overlap de servidor: 15/15
✓ Patrón de ID: 10/10

💡 Recomendación: ✅ Sin banderas de riesgo
```

### `/view_bans`
Muestra todos los banes registrados con paginación

### `/search_user <ID>`
Busca un usuario específico en los registros de baneo

## 📝 Formato del archivo `identity_data.txt`

```
[BAN]
ID: 123456789012345678
User: NombreUsuario#1234
Fecha: 2025-12-11 10:30:45
Servidor: 1433202195221713008
Historial: Descripción del historial
Notas: Notas adicionales del baneo
[/BAN]

[BAN]
ID: 987654321098765432
User: OtroUsuario#5678
Fecha: 2025-12-10 14:22:10
Servidor: 1433202195221713008
Historial: Más historial
Notas: Más notas
[/BAN]
```

## 🚀 Flujo de Funcionamiento

### Cuando alguien es baneado:
1. ✅ Evento `on_member_ban` se dispara
2. ✅ Bot lee la razón del baneo
3. ✅ Se registra en `identity_data.txt`
4. ✅ Embed se envía al canal de datos
5. ✅ Se guarda para análisis futuro

### Cuando alguien se une:
1. ✅ Evento `on_member_join` se dispara
2. ✅ Bot lee los banes registrados
3. ✅ Calcula Trust Score del nuevo miembro
4. ✅ Si score < 70, envía alerta al canal
5. ✅ Incluye razones y recomendaciones

## 🔍 Casos de Detección

### Detección de Alts
- Nombre muy similar al de un baneado
- Avatar idéntico
- ID de usuario muy cercano (< 100)
- Misma antigüedad de cuenta

### Detección de Ban Evaders
- Nombre con ligeras variaciones
- Avatar casi idéntico
- Cuenta nueva (< 30 días)
- Se unió poco después del baneo

## ⚙️ Configuración Avanzada

### Cambiar sensibilidad del Trust Score

En `trust_score.py`, ajusta los thresholds:

```python
# Para nombres más sensibles:
if similarity > 0.80:  # En lugar de 0.85
    penalty = 20

# Para IDs más sensibles:
if id_difference < 50:  # En lugar de 100
    penalty = 10
```

### Cambiar canales de alertas

En `events.py`:
```python
ALERT_CHANNEL_ID = 1234567890123456789  # Tu canal
DATA_CHANNEL_ID = 9876543210987654321   # Tu canal
```

## 🛡️ Seguridad y Privacidad

- ✅ Todos los datos se guardan localmente en un `.txt`
- ✅ No se usa base de datos externa
- ✅ Control total sobre el archivo
- ✅ Fácil de respaldar
- ✅ Sin dependencias de terceros

## 🐛 Solución de Problemas

### El bot no detecta banes
- Verifica que el bot tenga permiso de ban en el servidor
- Asegúrate de que `intents.guilds = True`

### Las alertas no llegan
- Verifica los IDs de canal en `events.py`
- Asegúrate de que el bot puede enviar mensajes a esos canales

### El archivo se corrompe
- Nunca edites `identity_data.txt` manualmente
- Usa los comandos del bot para gestionar banes

## 📌 Notas Importantes

- El archivo `identity_data.txt` se crea automáticamente
- Si lo borras, se creará uno nuevo vacío
- Los comandos solo funcionan con slash commands (`/check_trust`)
- El bot necesita permisos: Ver canales, Enviar mensajes, Leer historial

## 📞 Uso Recomendado

1. Configura los canales de alertas primero
2. Prueba con `/check_trust @alguien`
3. Verifica que los embeds se envíen correctamente
4. Monitorea los banes durante 1-2 semanas
5. Ajusta los thresholds según necesites

---

**Sistema creado para OxcyShop Discord Bot**
Última actualización: 2025-12-11
