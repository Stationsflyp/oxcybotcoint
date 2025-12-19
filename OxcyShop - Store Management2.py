import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import database  # Import database module

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # necesario para comandos
bot = commands.Bot(command_prefix="!", intents=intents)

import random
from discord.ext import commands

# Lista de emojis que el bot puede usar
EMOJIS = [
    "😎", "🔥", "💖", "✨", "🎉", "🤖", "😱", "😂",
    "💯", "🌟", "🥳", "🤩", "💥", "🦄", "🍀", "🍕",
    "🍩", "🍓", "🎶", "🏆", "🎯", "⚡", "🚀", "🛠️",
    "📦", "🪄", "🌈", "💌", "🫶", "👑", "🥰", "😜",
    "😇", "😏", "🤔", "🙌", "👏", "🤝", "💎", "🛒"
]


# Diccionario para llevar usuarios a los que se les debe reaccionar
reaction_users = set()  # user IDs

# Comando para agregar/quitar usuarios del sistema de reacción
@bot.command()
@commands.has_permissions(administrator=True)
async def reactuser(ctx, user: discord.Member = None, action: str = None):
    """
    !reactuser @user add -> Activar reacción para el usuario
    !reactuser @user remove -> Desactivar reacción para el usuario
    """
    if not user or not action or action.lower() not in ["add", "remove"]:
        await ctx.send("❌ Uso correcto: `!reactuser @user add` o `!reactuser @user remove`")
        return

    if action.lower() == "add":
        reaction_users.add(user.id)
        await ctx.send(f"✅ El bot ahora reaccionará automáticamente a los mensajes de {user.mention}")
    else:
        reaction_users.discard(user.id)
        await ctx.send(f"⚠️ El bot ya no reaccionará a los mensajes de {user.mention}")


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --------------------- USUARIOS ---------------------
OWNER_ID = 998836610516914236  # Owner con acceso total

CANAL_ID = 1449082898279043103  # ID del canal de bienvenida
BANNER_URL = "https://i.ibb.co/7JZnM4Hd/Gemini-Generated-Image-bosylebosylebosy.png"
BANNER_URL_OXCY_V2 = "https://i.ibb.co/kVyf2hFr/Screenshot-2025-12-12-122542.png"
BANNER_URL_ICON_V2 = "https://i.ibb.co/GQFJ0hrr/Fho-W-qg-BS96-Z4j1-Wuar-OQA.webp"


# --------------------- CANALES ---------------------
PREMIUM_UI_CHANNEL_ID = 1450555415673962678  # Canal donde se publican las Premium UI
LEADERBOARD_CHANNEL_ID = 1450555229719498946

# --------------------- VARIABLES ---------------------
message_history = {}    # user_id -> {"last_message": str, "last_time": datetime, "same_count": int, "spam_warn": int}
voice_join_times = {}   # user_id -> datetime (for voice currency)
spam_penalty = 5        # Monedas a quitar por spam

def similarity_ratio(a, b):
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 1.0
    matches = sum(1 for i, char in enumerate(a) if i < len(b) and char == b[i])
    return matches / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0





@bot.command()
@commands.has_permissions(administrator=True)
async def GUIX(ctx):
    """Comando para vender UI por monedas"""
    
    # 1. Ask for Cost
    prompt_cost = await ctx.send("💰 **¿Cuál es el precio en monedas? (Ej: 100)**")
    
    def check_cost(m):
        return m.author == ctx.author and m.content.isdigit()

    try:
        msg_cost = await bot.wait_for("message", timeout=60, check=check_cost)
        price = int(msg_cost.content)
        await msg_cost.delete()
        await prompt_cost.delete()
    except asyncio.TimeoutError:
        await ctx.send("⌛ Timeout. Comando cancelado.")
        return

    # 2. Ask for Image
    prompt_img = await ctx.send("📸 **Sube la imagen preview de la UI (60s)**")

    def check_img(m):
        return m.author == ctx.author and m.attachments

    try:
        msg_img = await bot.wait_for("message", timeout=60, check=check_img)
        if not msg_img.attachments:
            await ctx.send("❌ No se detectó ninguna imagen. Comando cancelado.")
            return

        img = msg_img.attachments[0].url
        await msg_img.delete()
        await prompt_img.delete()

        # 3. Post Embed
        embed = discord.Embed(
            title="👑 PREMIUM UI AVAILABLE | UI PREMIUM DISPONIBLE",
            description=f"✨ Click **Buy UI** to purchase access. | Haz click en **Comprar UI** para acceder.\n💰 Price: **{price} coins** | Precio: **{price} monedas**",
            color=0xD4AF37
        )
        embed.set_image(url=img)
        embed.add_field(name="⭐ Premium Quality | Calidad Premium", value="Exclusive Design • Fast Delivery • Full Support\nDiseño Exclusivo • Entrega Rápida • Soporte Completo", inline=False)
        embed.set_footer(text="OxcyShop • 👑 Colección Premium", icon_url=BANNER_URL_ICON_V2)
        embed.timestamp = discord.utils.utcnow()

        premium_ui_channel = bot.get_channel(PREMIUM_UI_CHANNEL_ID)
        if premium_ui_channel:
            sent_msg = await premium_ui_channel.send(embed=embed, view=BuyView())
            
            # 4. Save Price to DB
            database.add_guix_listing(sent_msg.id, price)
            
            await ctx.send(f"✅ UI Premium publicada por {price} monedas en {premium_ui_channel.mention}.")
        else:
            await ctx.send("❌ Premium UI channel not found!")

    except asyncio.TimeoutError:
        await ctx.send("⌛ Timeout. Comando cancelado.")
    except Exception as e:
        await ctx.send(f"❌ Error: {type(e).__name__} - {str(e)}")

class ClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim UI / Reclamar UI", style=discord.ButtonStyle.success, emoji="🎁", custom_id="persistent_claim_ui")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        await interaction.response.defer()
        
        delivery = database.get_ui_delivery(user_id)
        if not delivery:
            embed = discord.Embed(
                title="⏳ UI Not Available | UI No Disponible",
                description="Your UI is not ready yet. The owner is processing your request. | Tu UI aún no está lista. El owner está procesando tu solicitud.",
                color=0xFFA500
            )
            embed.set_footer(text="OxcyShop • Please wait | Por favor espera")
            embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        link, password, claimed = delivery
        
        if claimed == 1:
            embed = discord.Embed(
                title="✅ Already Claimed | Ya Reclamada",
                description="You already downloaded this UI before. | Ya descargaste esta UI anteriormente.",
                color=0xFF0000
            )
            embed.add_field(name="💡 Tip | Consejo", value="Check your download library. | Consulta tu biblioteca de descargas", inline=False)
            embed.set_footer(text="OxcyShop • Premium UI Store")
            embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎁 Your Premium UI is Ready! | ¡Tu UI Premium está lista!",
            description="Thank you for your purchase at OxcyShop. Here is your download: | Gracias por tu compra en OxcyShop. Aquí está tu descarga:",
            color=0xD4AF37
        )
        embed.add_field(name="📥 Download Link | Link de Descarga", value=f"[Click here | Click aquí]({link})", inline=False)
        embed.add_field(name="🔐 RAR Password | Contraseña RAR", value=f"`{password}`", inline=False)
        embed.set_footer(text="OxcyShop • Premium UI Store")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed, ephemeral=False)
        
        database.mark_ui_claimed(user_id)
        
        button.disabled = True
        await interaction.message.edit(view=self)
        
        log_channel = interaction.client.get_channel(1449082160471343168)
        if log_channel:
            log_embed = discord.Embed(
                title="📋 Claim Log | Log de Reclamación",
                description=f"**User | Usuario:** {interaction.user.mention}\n**ID:** `{user_id}`",
                color=0x00AA00
            )
            log_embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=log_embed)

class DeliveryModal(discord.ui.Modal, title="Deliver UI | Entregar UI"):
    link = discord.ui.TextInput(label="Download Link | Link de Descarga", placeholder="https://...", required=True)
    password = discord.ui.TextInput(label="RAR Password | Contraseña RAR", placeholder="Enter password | Ingresa la contraseña", required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = self.user_id
        link = str(self.link)
        password = str(self.password)
        
        try:
            database.save_ui_delivery(user_id, link, password)
            database.mark_ui_delivered(user_id)
            
            user = await interaction.client.fetch_user(user_id)
            embed = discord.Embed(
                title="🎁 Your Premium UI is Available | Tu UI Premium está Disponible",
                description="Click the button to claim and view your download. | Haz click en el botón para reclamar y ver tu descarga:",
                color=0xD4AF37
            )
            embed.set_footer(text="OxcyShop • Premium UI Store")
            embed.timestamp = discord.utils.utcnow()
            
            await user.send(embed=embed, view=ClaimView())
            await interaction.followup.send(f"✅ UI sent to | UI enviada a {user.mention}")
            
            self.deliver_button.disabled = True
            await interaction.message.edit(view=self.delivery_view)
        except Exception as e:
            await interaction.followup.send(f"❌ Error sending DM | Error enviando DM: {str(e)}")

class DeliveryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Deliver UI / Entregar UI", style=discord.ButtonStyle.success, emoji="🎁", custom_id="persistent_deliver_ui")
    async def deliver_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the owner can deliver UIs. | Solo el owner puede entregar UIs.", ephemeral=True)
            return
        
        user_id = None
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            if "**ID:**" in embed.description:
                try:
                    user_id = int(embed.description.split("**ID:** `")[1].split("`")[0])
                except Exception as e:
                    print(f"Error parsing user_id: {e}, description: {embed.description}")
                    pass
        
        if not user_id:
            await interaction.response.send_message("❌ Could not extract user ID. | No se pudo extraer el ID del usuario.", ephemeral=True)
            return
        
        modal = DeliveryModal()
        modal.user_id = user_id
        modal.deliver_button = button
        modal.delivery_view = self
        await interaction.response.send_modal(modal)

class BuyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Comprar UI / Buy UI", style=discord.ButtonStyle.success, custom_id="persistent_buy_ui")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            message_id = interaction.message.id
            
            price = database.get_guix_price(message_id)
            if not price:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description="No se encontró el precio de este UI.",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            
            user_coins = database.get_coins(user_id)
            if user_coins < price:
                missing_coins = price - user_coins
                embed = discord.Embed(
                    title="💸 Insufficient Coins | Monedas Insuficientes",
                    description="You don't have enough coins to buy this UI. | No tienes suficientes monedas para comprar este UI.",
                    color=0xFF6B00
                )
                embed.add_field(name="💰 Required Price | Precio Requerido", value=f"`{price}` coins", inline=True)
                embed.add_field(name="💰 Your Balance | Tu Balance", value=f"`{user_coins}` coins", inline=True)
                embed.add_field(name="❌ Missing | Te Faltan", value=f"`{missing_coins}` coins", inline=True)
                embed.set_footer(text="OxcyShop • Gana más monedas en el servidor")
                embed.timestamp = discord.utils.utcnow()
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            database.remove_coins(user_id, price)
            
            claim_channel = interaction.client.get_channel(1450952100929605664)
            if claim_channel:
                img_url = None
                if interaction.message.embeds:
                    img_url = interaction.message.embeds[0].image.url if interaction.message.embeds[0].image else None
                
                embed = discord.Embed(
                    title="📦 Nueva Solicitud de UI",
                    description=f"**Usuario:** {interaction.user.mention}\n**ID:** `{user_id}`\n**Precio:** `{price}` coins",
                    color=0xD4AF37
                )
                if img_url:
                    embed.set_image(url=img_url)
                embed.timestamp = discord.utils.utcnow()
                
                await claim_channel.send(embed=embed, view=DeliveryView())
            
            success_embed = discord.Embed(
                title="✅ Purchase Successful! | ¡Compra Exitosa!",
                description="Your request has been registered correctly. | Tu solicitud ha sido registrada correctamente.",
                color=0x00AA00
            )
            success_embed.add_field(name="💰 Coins Deducted | Coins Deducidos", value=f"`{price}` coins", inline=True)
            success_embed.add_field(name="💰 New Balance | Nuevo Balance", value=f"`{database.get_coins(user_id)}` coins", inline=True)
            success_embed.add_field(name="📬 Next Step | Próximo Paso", value="You will receive the data in your DM when the owner confirms. | Recibirás los datos en tu DM cuando el owner confirme", inline=False)
            success_embed.set_footer(text="OxcyShop • Premium UI Store")
            success_embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(embed=success_embed, ephemeral=True)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error en la compra",
                description=f"Ocurrió un problema: {str(e)}",
                color=0xFF0000
            )
            error_embed.set_footer(text="OxcyShop • Contacta al owner")
            error_embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(embed=error_embed, ephemeral=True)

REACT_USERS = [998836610516914236, 1384032725014548591]  # coloca los IDs reales aquí

# Función para crear el embed
def crear_embed(usuario):
    embed = discord.Embed(
        title="Welcome to OxcyShop | ¡Bienvenido a OxcyShop - Tu Tienda de Diseños UI!",
        description=(
            f"Hello {usuario.mention}, we're thrilled to have you here! | ¡Hola {usuario.mention}, nos alegra mucho tenerte aquí! 🎨\n\n"
            "✨ Explore our channels and discover stunning UI designs. | Explora nuestros canales y descubre hermosos diseños UI.\n"
            "💖 Join the community, share your ideas and have fun! | Únete a la comunidad, comparte tus ideas ¡y diviértete!"
        ),
        color=0xFF69B4
    )
    # Thumbnail = avatar del usuario
    embed.set_thumbnail(url=usuario.avatar.url)

    # Imagen grande del banner
    embed.set_image(url=BANNER_URL)

    # Footer bilingüe
    embed.set_footer(text="Thank you for joining OxcyShop! | ¡Gracias por unirte a OxcyShop! 🌸")
    embed.timestamp = discord.utils.utcnow()
    return embed

# Evento real de bienvenida
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_ID)
    embed = crear_embed(member)

    # Botones interactivos
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Server Link", url="https://discord.gg/MRpKn5T2bs"))
    view.add_item(discord.ui.Button(label="Contact Us", url="https://discord.com/users/998836610516914236"))

    await canal.send(embed=embed, view=view)


# En el on_ready envías el botón al canal service
status_messages = [
    ("🛒 Store Management", discord.ActivityType.watching),
    ("💳 Processing Orders", discord.ActivityType.watching),
    ("🎨 UI Designs", discord.ActivityType.watching),
    ("📦 Deliveries", discord.ActivityType.watching),
    ("💰 Payments", discord.ActivityType.watching),
    ("👥 Customers", discord.ActivityType.watching),
    ("📊 Store Stats", discord.ActivityType.watching),
    ("🔐 Security", discord.ActivityType.watching),
    ("⚡ Fast Service", discord.ActivityType.watching),
    ("🌟 Quality Designs", discord.ActivityType.watching),
    ("🚀 OxcyShop", discord.ActivityType.watching),
]
current_status_index = 0

async def change_status():
    global current_status_index
    while True:
        status_name, status_type = status_messages[current_status_index]
        activity = discord.Activity(type=status_type, name=status_name)
        await bot.change_presence(status=discord.Status.online, activity=activity)
        current_status_index = (current_status_index + 1) % len(status_messages)
        await asyncio.sleep(10)

LEADERBOARD_CHANNEL_ID = 1450555229719498946

async def update_leaderboard():
    await bot.wait_until_ready()
    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if not channel:
        print("❌ Leaderboard channel not found")
        return

    while not bot.is_closed():
        try:
            top_users = database.get_top_users(10)
            
            description = ""
            for i, (user_id, coins) in enumerate(top_users, 1):
                user = bot.get_user(user_id)
                username = user.name if user else f"User {user_id}"
                description += f"**#{i}** {username} - 💰 `{coins}` coins\n"
            
            if not description:
                description = "No data yet."

            embed = discord.Embed(
                title="🏆 Global Currency Leaderboard",
                description=description,
                color=0xFFD700
            )
            embed.set_footer(text="Updates every minute • OxcyShop")
            embed.timestamp = discord.utils.utcnow()

            # Check if we have a stored message ID
            message_id = database.get_config("leaderboard_message_id")
            
            if message_id:
                try:
                    msg = await channel.fetch_message(int(message_id))
                    # Only edit if the bot authored the message
                    if msg.author.id == bot.user.id:
                        await msg.edit(embed=embed)
                    else:
                        # Message was not authored by bot, delete and send new one
                        await msg.delete()
                        msg = await channel.send(embed=embed)
                        database.set_config("leaderboard_message_id", msg.id)
                except discord.NotFound:
                    message_id = None # Message deleted, send new one
            
            if not message_id:
                msg = await channel.send(embed=embed)
                database.set_config("leaderboard_message_id", msg.id)
                
        except Exception as e:
            print(f"Error updating leaderboard: {e}")
        
        await asyncio.sleep(60) # Update every 60 seconds

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    
    # Initialize Database
    database.init_db()
    print("✅ Database initialized")

    # Sync Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")
    
    # Registrar vistas persistentes
    bot.add_view(BuyView())
    bot.add_view(DeliveryView())
    bot.add_view(ClaimView())

    bot.loop.create_task(change_status())
    bot.loop.create_task(update_leaderboard())
    
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


# Comando de prueba
@bot.command()
async def test(ctx):
    """Envía el embed de bienvenida usando tu perfil para pruebas"""
    embed = crear_embed(ctx.author)

    # Botones interactivos
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Catalog | Ver Catálogo", url="https://discord.com/channels/1286045119715475527/1449082718393733150"))
    view.add_item(discord.ui.Button(label="Contact Us | Contacto", url="https://discord.com/users/998836610516914236"))

    await ctx.send(embed=embed, view=view)




@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    user_id = member.id
    current_time = discord.utils.utcnow()

    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        voice_join_times[user_id] = current_time
    
    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        if user_id in voice_join_times:
            join_time = voice_join_times.pop(user_id)
            duration = (current_time - join_time).total_seconds()
            
            # Award coins: 1 coin per minute (adjust as needed)
            minutes = int(duration // 60)
            if minutes > 0:
                coins_earned = minutes * 2  # 2 coins per minute
                database.add_coins(user_id, coins_earned)
                # print(f"User {member} earned {coins_earned} coins for {minutes} mins in voice.")

    # User switched channels (optional: treat as continuous or reset)
    # For simplicity, we treat switch as continuous if we don't pop the time, 
    # but if we want to be precise we could calculate and reset.
    # Current logic only handles Join -> Leave. 
    # If they switch, before.channel is NOT None and after.channel is NOT None.
    # We do nothing, so the timer keeps running.

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    current_time = discord.utils.utcnow()

    # --- CURRENCY SYSTEM (CHAT) ---
    if not message.author.bot and message.content.strip():
        if user_id not in message_history:
            message_history[user_id] = {"last_message": "", "last_time": current_time, "same_count": 0, "spam_warn": 0}
        
        history = message_history[user_id]
        time_diff = (current_time - history["last_time"]).total_seconds()
        
        similarity = similarity_ratio(message.content, history["last_message"])
        
        if time_diff > 10:
            history["same_count"] = 0
        
        if similarity >= 0.85 and time_diff < 5:
            history["same_count"] += 1
            
            if history["same_count"] >= 3:
                history["spam_warn"] += 1
                current_coins = database.get_coins(user_id)
                coins_to_remove = min(spam_penalty, current_coins)
                database.remove_coins(user_id, coins_to_remove)
                
                embed = discord.Embed(
                    title="⚠️ Spam Detected | Spam Detectado",
                    description=f"{message.author.mention} Stop spamming! You've been penalized. | ¡Deja de spamear! Has sido penalizado.",
                    color=0xFF0000
                )
                embed.add_field(name="❌ Coins Removed | Monedas Removidas", value=f"`{coins_to_remove}` coins", inline=True)
                embed.add_field(name="💰 New Balance | Nuevo Balance", value=f"`{database.get_coins(user_id)}` coins", inline=True)
                embed.add_field(name="⚠️ Spam Warnings | Advertencias de Spam", value=f"`{history['spam_warn']}`", inline=True)
                embed.set_footer(text="OxcyShop • No spam allowed | No se permite spam")
                embed.timestamp = discord.utils.utcnow()
                
                await message.channel.send(embed=embed)
                
                history["same_count"] = 0
        else:
            history["same_count"] = 0
        
        history["last_message"] = message.content
        history["last_time"] = current_time

    # --- REACCIONES AUTOMÁTICAS A USUARIOS ESPECÍFICOS ---
    if user_id in REACT_USERS or user_id in reaction_users:
        try:
            num_emojis = random.randint(1, 3)
            emojis_to_use = random.sample(EMOJIS, k=num_emojis)  # Evita repetir emojis en el mismo mensaje
            for emoji in emojis_to_use:
                await asyncio.sleep(random.uniform(2.0, 5.0)) # Delay aumentado para evitar rate limits
                await message.add_reaction(emoji)
        except Exception as e:
            print(f"Error adding reaction: {e}")

    # --- Procesar comandos SOLO una vez al final ---
    await bot.process_commands(message)

# --- SLASH COMMANDS ---

@bot.tree.command(name="shop", description="Sell a UI for coins | Vender una UI por monedas (Staff Only | Solo Staff)")
@discord.app_commands.describe(price="Price in coins | Precio en monedas", image="Preview image of the UI | Imagen previa de la UI")
async def shop(interaction: discord.Interaction, price: int, image: discord.Attachment):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You are not authorized to use this command. | No estás autorizado para usar este comando.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        img_url = image.url

        embed = discord.Embed(
            title="👑 PREMIUM UI AVAILABLE | UI PREMIUM DISPONIBLE",
            description=f"✨ Click **Buy UI** to purchase access. | Haz click en **Comprar UI** para acceder.\n💰 Price: **{price} coins** | Precio: **{price} monedas**",
            color=0xD4AF37
        )
        embed.set_image(url=img_url)
        embed.add_field(name="⭐ Premium Quality | Calidad Premium", value="Exclusive Design • Fast Delivery • Full Support\nDiseño Exclusivo • Entrega Rápida • Soporte Completo", inline=False)
        embed.set_footer(text="OxcyShop • 👑 Premium Collection | Colección Premium", icon_url=BANNER_URL_ICON_V2)
        embed.timestamp = discord.utils.utcnow()

        premium_ui_channel = bot.get_channel(PREMIUM_UI_CHANNEL_ID)
        if premium_ui_channel:
            sent_msg = await premium_ui_channel.send(embed=embed, view=BuyView())
            
            # Save Price to DB
            database.add_guix_listing(sent_msg.id, price)
            
            await interaction.followup.send(f"✅ Premium UI published for {price} coins in {premium_ui_channel.mention} | UI Premium publicada por {price} monedas en {premium_ui_channel.mention}")
        else:
            await interaction.followup.send("❌ Premium UI channel not found! | ¡Canal de UI Premium no encontrado!")

    except Exception as e:
        await interaction.followup.send(f"❌ Error | Error: {str(e)}")

@bot.tree.command(name="monedas", description="Send coins to another user | Envía monedas a otro usuario")
@discord.app_commands.describe(usuario="User receiving coins | Usuario que recibe las monedas", cantidad="Amount of coins | Cantidad de monedas")
async def monedas(interaction: discord.Interaction, usuario: discord.User, cantidad: int):
    await interaction.response.defer(ephemeral=True)
    
    if interaction.user.id != OWNER_ID:
        await interaction.followup.send("❌ Only the owner can use this command. | Solo el owner puede usar este comando.", ephemeral=True)
        return
    
    if cantidad <= 0:
        await interaction.followup.send("❌ The amount must be greater than 0. | La cantidad debe ser mayor a 0.", ephemeral=True)
        return
    
    if usuario.bot:
        await interaction.followup.send("❌ You cannot give coins to bots. | No puedes dar monedas a bots.", ephemeral=True)
        return
    
    database.add_coins(usuario.id, cantidad)
    
    embed = discord.Embed(
        title="💰 Coins Received | Monedas Recibidas",
        description=f"{usuario.mention} has received **{cantidad}** coins from {interaction.user.mention} | {usuario.mention} ha recibido **{cantidad}** monedas de {interaction.user.mention}",
        color=0xD4AF37
    )
    embed.add_field(name="💰 New Balance | Nuevo Balance", value=f"`{database.get_coins(usuario.id)}` coins", inline=False)
    embed.set_footer(text="OxcyShop • Coin System | Sistema de Monedas")
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.followup.send(embed=embed)

bot.run(TOKEN)
