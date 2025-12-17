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
coin_cooldowns = {}     # user_id -> datetime (for chat currency)
voice_join_times = {}   # user_id -> datetime (for voice currency)



# --------------------- CLASES PARA FREE UI ---------------------

class ReceiveUIView(discord.ui.View):
    def __init__(self, target_user_id: int, content: str, password: str, staff_member_id: int, staff_name: str):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id
        self.content = content
        self.password = password
        self.staff_member_id = staff_member_id
        self.staff_name = staff_name

    @discord.ui.button(label="✅ Confirmar Recepción", style=discord.ButtonStyle.green, custom_id="receive_ui_confirm")
    async def receive(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user_id:
            await interaction.response.send_message("❌ Este botón no es para ti.", ephemeral=True)
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        reveal_embed = discord.Embed(
            title="🔓 Your UI Details",
            description="Your UI details are now revealed:",
            color=0x00FFD5
        )
        reveal_embed.add_field(name="🔗 Download Link", value=self.content, inline=False)
        reveal_embed.add_field(name="🔐 RAR Password", value=f"`{self.password}`", inline=True)
        reveal_embed.set_footer(text="OxcyShop • Delivery Complete")
        reveal_embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=reveal_embed, ephemeral=True)

        log_channel = interaction.client.get_channel(FREE_UI_LOGS_ID)
        if log_channel:
            staff_user = interaction.client.get_user(self.staff_member_id)
            staff_mention = staff_user.mention if staff_user else f"<@{self.staff_member_id}>"
            
            log_embed = discord.Embed(
                title="✅ UI DELIVERED",
                description=f"**Recipient:** {interaction.user.mention}\n**Staff:** {staff_mention}",
                color=0x00FF00
            )
            log_embed.add_field(name="🔗 Link/Content", value=self.content, inline=False)
            log_embed.add_field(name="🔐 RAR Password", value=f"`{self.password}`", inline=True)
            log_embed.set_footer(text="OxcyShop • Delivery Log")
            log_embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=log_embed)

        button.disabled = True
        await interaction.message.edit(view=self)

class DeliveryModal(discord.ui.Modal, title="Deliver UI"):
    content = discord.ui.TextInput(label="Download Link / Content", style=discord.TextStyle.paragraph, placeholder="Paste the link or content here...")
    rar_password = discord.ui.TextInput(label="RAR Password", required=False, default="2315", placeholder="Leave empty for default (2315)")

    def __init__(self, target_user: discord.User, ui_image_url: str, original_message: discord.Message):
        super().__init__()
        self.target_user = target_user
        self.ui_image_url = ui_image_url
        self.original_message = original_message

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        
        password = self.rar_password.value or "2315"
        content_to_send = self.content.value
        
        try:
            embed = discord.Embed(
                title="📦 Your UI is Ready!",
                description=f"Hello {self.target_user.mention}, the staff has approved your request! 🎉\n\n**Click the button below to reveal your download link and RAR password.**",
                color=0x00FFD5
            )
            embed.add_field(name="⚠️ Important", value="Click '✅ Confirmar Recepción' to reveal your download link and RAR password.", inline=False)
            embed.set_footer(text="OxcyShop • Approved by Staff")
            embed.timestamp = discord.utils.utcnow()
            
            if self.ui_image_url:
                embed.set_image(url=self.ui_image_url)
            
            view = ReceiveUIView(self.target_user.id, content_to_send, password, interaction.user.id, interaction.user.name)
            await self.target_user.send(embed=embed, view=view)
            
            approved_embed = self.original_message.embeds[0]
            approved_embed.color = 0x00FF00
            approved_embed.title = "✅ FREE UI CLAIM - APPROVED"
            approved_embed.add_field(name="Approved by", value=interaction.user.mention, inline=True)
            
            await self.original_message.edit(embed=approved_embed, view=None)

            await interaction.followup.send(f"✅ UI sent to {self.target_user.mention}! Waiting for user confirmation...", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send(f"❌ Could not DM {self.target_user.mention}. They might have DMs blocked.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class AdminClaimView(discord.ui.View):
    def __init__(self, target_user_id: int, ui_image_url: str):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id
        self.ui_image_url = ui_image_url

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="admin_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        target_user = interaction.guild.get_member(self.target_user_id)
        if not target_user:
            # Try to fetch if not in cache
            try:
                target_user = await interaction.client.fetch_user(self.target_user_id)
            except:
                await interaction.response.send_message("❌ User not found.", ephemeral=True)
                return

        await interaction.response.send_modal(DeliveryModal(target_user, self.ui_image_url, interaction.message))

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="admin_reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        target_user = interaction.guild.get_member(self.target_user_id)
        if not target_user:
            try:
                target_user = await interaction.client.fetch_user(self.target_user_id)
            except:
                pass

        # Enviar DM de rechazo
        if target_user:
            try:
                reject_dm = discord.Embed(
                    title="❌ UI Request Update",
                    description=f"Hello {target_user.mention}, unfortunately your request for the UI has been declined.",
                    color=0xFF0000
                )
                reject_dm.add_field(
                    name="ℹ️ Note", 
                    value="This does not mean you cannot request other UIs in the future. Feel free to browse our other available designs!",
                    inline=False
                )
                reject_dm.set_footer(text="OxcyShop • UI Request Status")
                reject_dm.timestamp = discord.utils.utcnow()
                
                if self.ui_image_url:
                    reject_dm.set_thumbnail(url=self.ui_image_url)
                
                await target_user.send(embed=reject_dm)
            except discord.Forbidden:
                pass # No se pudo enviar DM

        # Actualizar embed a rojo
        rejected_embed = interaction.message.embeds[0]
        rejected_embed.color = 0xFF0000 # Red
        rejected_embed.title = "❌ FREE UI CLAIM - REJECTED"
        rejected_embed.add_field(name="Rejected by", value=interaction.user.mention, inline=True)
        
        await interaction.message.edit(embed=rejected_embed, view=None)
        await interaction.response.send_message("❌ Claim rejected and user notified.", ephemeral=True)

class ClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🆓 Claim GUI", style=discord.ButtonStyle.green, custom_id="persistent_claim_gui")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        message_id = interaction.message.id
        
        if user.id != OWNER_ID:
            if user.id in claim_cooldowns:
                last_claim_time = claim_cooldowns[user.id]
                time_diff = discord.utils.utcnow() - last_claim_time
                if time_diff.total_seconds() < 3 * 3600:
                    remaining_time = 3 * 3600 - time_diff.total_seconds()
                    hours = int(remaining_time // 3600)
                    minutes = int((remaining_time % 3600) // 60)
                    await interaction.followup.send(
                        f"⏳ Please wait **{hours}h {minutes}m** before claiming another UI.",
                        ephemeral=True
                    )
                    return

        if user.id in freeui_claims and freeui_claims[user.id] == message_id:
            await interaction.followup.send("⚠️ Ya has reclamado esta UI.", ephemeral=True)
            return

        img_url = None
        if interaction.message.embeds:
            img_url = interaction.message.embeds[0].image.url

        log_channel = interaction.client.get_channel(FREE_UI_LOGS_ID)
        if log_channel:
            embed = discord.Embed(
                title="📝 NEW FREE UI CLAIM",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Channel:** {interaction.channel.mention}",
                color=0xFFFF00
            )
            if img_url:
                embed.set_thumbnail(url=img_url)
                embed.set_image(url=img_url)
            
            embed.add_field(name="Source Message", value=f"[Jump to Message]({interaction.message.jump_url})", inline=False)
            embed.set_footer(text="OxcyShop • Claim Review")
            embed.timestamp = discord.utils.utcnow()

            view = AdminClaimView(user.id, img_url)
            await log_channel.send(embed=embed, view=view)
            
            await interaction.followup.send(
                "**✅ Request Sent!**\nPlease wait for staff approval.\n**✅ ¡Solicitud Enviada!**\nPor favor espera la aprobación del staff.",
                ephemeral=True
            )
            
            freeui_claims[user.id] = message_id
            claim_cooldowns[user.id] = discord.utils.utcnow()
        else:
            await interaction.followup.send("❌ Log channel not configured.", ephemeral=True)

class BuyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Buy UI", style=discord.ButtonStyle.blurple, custom_id="persistent_buy_gui")
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        message_id = interaction.message.id
        
        price = database.get_guix_price(message_id)
        if price is None:
            await interaction.response.send_message("❌ Error: Price not found for this item.", ephemeral=True)
            return

        # Confirmation Dialog
        embed = discord.Embed(
            title="💸 Confirm Purchase",
            description=f"Are you sure you want to buy this UI for **{price} coins**?",
            color=0xFFA500
        )
        embed.set_footer(text=f"Current Balance: {database.get_coins(user.id)} coins")
        
        view = ConfirmBuyView(price, message_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmBuyView(discord.ui.View):
    def __init__(self, price, original_message_id):
        super().__init__(timeout=60)
        self.price = price
        self.original_message_id = original_message_id

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if database.remove_coins(user.id, self.price):
            # Success
            await interaction.response.edit_message(content="✅ Payment successful! Request sent to staff.", embed=None, view=None)
            
            # Handle the "delivery" request to staff
            # We need to find the original message to get the image
            try:
                original_message = await interaction.channel.fetch_message(self.original_message_id)
                img_url = original_message.embeds[0].image.url if original_message.embeds else None
                
                # Send to logs
                log_channel = interaction.client.get_channel(FREE_UI_LOGS_ID)
                if log_channel:
                    embed = discord.Embed(
                        title="💰 PAID UI CLAIM",
                        description=f"**User:** {user.mention} (`{user.id}`)\n**Price Paid:** {self.price} coins\n**Channel:** {interaction.channel.mention}",
                        color=0x00FF00 # Green for paid
                    )
                    if img_url:
                        embed.set_thumbnail(url=img_url)
                        embed.set_image(url=img_url)
                    
                    embed.add_field(name="Source Message", value=f"[Jump to Message]({original_message.jump_url})", inline=False)
                    embed.set_footer(text="OxcyShop • Paid Claim")
                    embed.timestamp = discord.utils.utcnow()

                    view = AdminClaimView(user.id, img_url)
                    await log_channel.send(embed=embed, view=view)
            except Exception as e:
                print(f"Error processing paid claim: {e}")
                
        else:
            # Insufficient funds
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description="You do not have enough coins to purchase this UI.",
                color=0xFF0000
            )
            embed.add_field(name="Required", value=f"{self.price} coins", inline=True)
            embed.add_field(name="Balance", value=f"{database.get_coins(user.id)} coins", inline=True)
            embed.add_field(name="How to earn?", value="Be active in chat and voice channels to earn coins!", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)

# --------------------- COMANDO STAFF: !freeui ---------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def freeui(ctx):
    """Comando para subir Free UI"""
    prompt_msg = await ctx.send("📸 **Sube la imagen preview de la UI (60s)**")

    def check(m):
        return m.author == ctx.author and m.attachments

    try:
        msg = await bot.wait_for("message", timeout=60, check=check)
        # Confirmamos que el attachment existe
        if not msg.attachments:
            await ctx.send("❌ No se detectó ninguna imagen. Comando cancelado.")
            return

        img = msg.attachments[0].url

        # Eliminamos el mensaje de prompt original para no spamear
        await prompt_msg.delete()

        embed = discord.Embed(
            title="🆓 FREE UI AVAILABLE",
            description="Click **Claim GUI** to request access.\nApproval required.",
            color=0x00FFD5
        )
        embed.set_image(url=img)
        embed.set_footer(text="OxcyShop • Free UI")

        free_ui_channel = bot.get_channel(FREE_UI_CHANNEL_ID)
        if free_ui_channel:
            await free_ui_channel.send(embed=embed, view=ClaimView())
        else:
            await ctx.send("❌ Free UI channel not found!")

    except asyncio.TimeoutError:
        await ctx.send("⌛ Timeout. Comando cancelado.")
    except Exception as e:
        await ctx.send(f"❌ Error: {type(e).__name__} - {str(e)}")

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
            title="👑 PREMIUM UI AVAILABLE",
            description=f"✨ Click **Buy UI** to purchase access.\n💰 Price: **{price} coins**",
            color=0xD4AF37
        )
        embed.set_image(url=img)
        embed.add_field(name="⭐ Premium Quality", value="Exclusive Design • Fast Delivery • Full Support", inline=False)
        embed.set_footer(text="OxcyShop • 👑 Premium Collection", icon_url=BANNER_URL_ICON_V2)
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

REACT_USERS = [998836610516914236, 1384032725014548591]  # coloca los IDs reales aquí

# Función para crear el embed
def crear_embed(usuario):
    embed = discord.Embed(
        title="Welcome to OxcyShop - Your UI Design Playground!",
        description=(
            f"Hello {usuario.mention}, we are thrilled to have you here! 🎨\n\n"
            "✨ Explore our channels and discover stunning UI designs.\n"
            "💖 Join the community, share your ideas, and have fun!"
        ),
        color=0xFF69B4
    )
    # Thumbnail = avatar del usuario
    embed.set_thumbnail(url=usuario.avatar.url)

    # Imagen grande del banner
    embed.set_image(url=BANNER_URL)

    # Footer en coreano
    embed.set_footer(text="서버에 오신 것을 환영합니다! 🌸 (Thank you for joining!)")
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


# ------------------- FASE TIENDA / ORDERS CON MODAL CORREGIDO -------------------

SERVICE_CHANNEL_ID = 1449082591071174760
LOGS_CHANNEL_ID = 1449087592078508032
ORDERS_CHANNEL_ID = 1449082387098112020

# Datos de la tienda

pending_orders = {}
user_channels = {}
spam_tracker = {}
SPAM_THRESHOLD = 5
SPAM_TIME_WINDOW = 5

# Definición de productos de la tienda
TIENDA_UI = [
    {"nombre": "Minimal UI", "precio": "$10"},
    {"nombre": "Dark Mode UI", "precio": "$15"},
    {"nombre": "Oxcy Dashboard", "precio": "$20"},
    # Agrega más productos según tu tienda
]


class ConfirmOrderView(discord.ui.View):
    def __init__(self, user_id, channel_id, order_data):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id
        self.order_data = order_data
    
    @discord.ui.button(label="✅ Confirm Order", style=discord.ButtonStyle.green, custom_id="confirm_order")
    async def confirm_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        pending_orders[self.user_id] = {
            "channel_id": self.channel_id,
            "order_data": self.order_data,
            "user": interaction.user
        }
        
        embed = discord.Embed(
            title="💳 PAYMENT METHODS",
            description="Choose your preferred payment method below and send the payment to the corresponding address/account.",
            color=0x6B5B95
        )
        
        embed.add_field(
            name="💵 Fiat Payment Methods",
            value="━━━━━━━━━━━━━━━━━━━",
            inline=False
        )
        
        embed.add_field(
            name="📱 Zelle",
            value="`+19295365930`",
            inline=False
        )
        
        embed.add_field(
            name="💰 CashApp",
            value="`anitap666`",
            inline=False
        )
        
        embed.add_field(
            name="💎 Cryptocurrency",
            value="━━━━━━━━━━━━━━━━━━━",
            inline=False
        )
        
        embed.add_field(
            name="Ξ Ethereum",
            value="`Coming Soon` ⏳",
            inline=False
        )
        
        embed.add_field(
            name="◎ Solana",
            value="`Coming Soon` ⏳",
            inline=False
        )
        
        embed.add_field(
            name="₿ Bitcoin",
            value="`Coming Soon` ⏳",
            inline=False
        )
        
        embed.add_field(
            name="🪙 USDT",
            value="`Coming Soon` ⏳",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ IMPORTANT",
            value="**DO NOT WRITE** - Only reply with your payment proof (screenshot or photo). Do not send any other messages.",
            inline=False
        )
        
        embed.set_footer(text="OxcyShop - Complete your purchase securely", icon_url=BANNER_URL_ICON_V2)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="❌ Cancel Order", style=discord.ButtonStyle.red, custom_id="cancel_order")
    async def cancel_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user_id in pending_orders:
            del pending_orders[self.user_id]
        
        embed = discord.Embed(
            title="❌ Order Cancelled",
            description="Your order has been cancelled.",
            color=0xFF0000
        )
        embed.set_footer(text="We hope to see you again!")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

# Modal para que el usuario ingrese el pedido
class OrderModal(discord.ui.Modal, title="🛒 OxcyShop - Place Your Order"):
    ui_name = discord.ui.TextInput(label="UI Name", placeholder="Enter the name of the UI")
    payment_method = discord.ui.TextInput(label="$ UIX Price", placeholder="$ Add UI Price")

    async def on_submit(self, interaction: discord.Interaction):
        print(f"\n=== MODAL CALLBACK STARTED ===")
        print(f"User: {interaction.user}")
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        ui_name = self.ui_name.value
        payment_method = self.payment_method.value

        print(f"UI Name: {ui_name}")
        print(f"UIX Price: {payment_method}")

        # Buscar precio automáticamente
        price = "N/A"
        for item in TIENDA_UI:
            if item["nombre"].lower() == ui_name.lower():
                price = item["precio"]
                break

        print(f"Price found: {price}")

        try:
            print(f"Fetching orders channel: {ORDERS_CHANNEL_ID}")
            orders_channel = bot.get_channel(ORDERS_CHANNEL_ID)
            print(f"Orders channel: {orders_channel}")
            
            if not orders_channel:
                print(f"ERROR: Channel not found!")
                await interaction.followup.send(
                    "❌ Orders channel not found.", 
                    ephemeral=True
                )
                return

            print(f"Creating order embed for orders channel...")
            order_embed = discord.Embed(
                title="📦 NEW ORDER RECEIVED",
                description=f"**Customer**: {user.mention}\n**Status**: ⏳ Awaiting Confirmation",
                color=0xFF6B9D
            )
            order_embed.add_field(name="🎨 Product", value=f"```{ui_name}```", inline=True)
            order_embed.add_field(name="💰 Payment Method", value=f"```{price}```", inline=True)
            order_embed.add_field(name="💳 UIX Price", value=f"```{payment_method}```", inline=True)
            order_embed.add_field(name="👤 Customer ID", value=f"```{user.id}```", inline=False)
            order_embed.set_thumbnail(url=user.avatar.url)
            order_embed.set_footer(text="OxcyShop - Store Management", icon_url=BANNER_URL_ICON_V2)
            order_embed.timestamp = discord.utils.utcnow()
            
            print(f"Sending order message...")
            order_message = await orders_channel.send(embed=order_embed)
            print(f"Order message sent: {order_message.id}")

            print(f"Creating private channel...")
            guild = orders_channel.guild
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            
            private_channel = await guild.create_text_channel(
                name=f"order-{user.name.lower()}",
                overwrites=overwrites
            )
            print(f"Private channel created: {private_channel.id}")

            print(f"Creating channel embed...")
            channel_embed = discord.Embed(
                title="🛍️ ORDER CONFIRMATION",
                description=f"Hello {user.mention}! 👋\n\nPlease review your order details below and confirm to proceed with payment.",
                color=0xFF6B9D
            )
            channel_embed.add_field(name="📦 Product Selected", value=f"**{ui_name}**", inline=False)
            channel_embed.add_field(name="💰 Payment Method", value=f"**{price}**", inline=True)
            channel_embed.add_field(name="💳 UIX Price", value=f"**{payment_method}**", inline=True)
            channel_embed.add_field(name="📋 Order Instructions", value="✅ Click the **Confirm Order** button to proceed\n❌ Click the **Cancel Order** button to cancel", inline=False)
            channel_embed.set_thumbnail(url=user.avatar.url)
            channel_embed.set_footer(text="OxcyShop - Complete your purchase", icon_url=BANNER_URL_ICON_V2)
            channel_embed.timestamp = discord.utils.utcnow()

            print(f"Sending message to private channel...")
            order_data = {
                "ui_name": ui_name,
                "price": price,
                "payment_method": payment_method
            }
            view = ConfirmOrderView(user.id, private_channel.id, order_data)
            await private_channel.send(embed=channel_embed, view=view)
            print(f"Channel message sent")
            
            user_channels[user.id] = private_channel.id
            print(f"Saved channel mapping for user {user.id}: {private_channel.id}")

            print(f"Sending confirmation to user...")
            confirmation_embed = discord.Embed(
                title="✅ Order Channel Created",
                description=f"Your private order channel has been created: {private_channel.mention}",
                color=0x00FF00
            )
            confirmation_embed.set_footer(text="OxcyShop - Order Management")
            await interaction.followup.send(
                embed=confirmation_embed, 
                ephemeral=True
            )
            print(f"=== MODAL CALLBACK COMPLETED SUCCESSFULLY ===\n")

        except discord.Forbidden as e:
            print(f"ERROR: Bot doesn't have permission: {str(e)}")
            await interaction.followup.send(
                "❌ I don't have permission to create channels. Check my permissions.", 
                ephemeral=True
            )
        except Exception as e:
            print(f"ERROR in callback: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ Error creating order: {type(e).__name__}: {str(e)}", 
                ephemeral=True
            )

# Vista con botón que abre el modal
class StartBuyingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Place Order", style=discord.ButtonStyle.blurple, custom_id="start_buy")
    async def start_buying(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.response.is_done():
            return

        print(f"Button clicked by {interaction.user}")
        try:
            modal = OrderModal()
            await interaction.response.send_modal(modal)
            print(f"Modal sent to {interaction.user}")
        except discord.HTTPException as e:
            if e.code == 40060:
                print(f"⚠️ Interaction already acknowledged for {interaction.user} (ignoring)")
            else:
                print(f"❌ Error sending modal: {e}")

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
                    await msg.edit(embed=embed)
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
    
    # Registrar vistas persistentes (solo una vez)
    if not hasattr(bot, 'persistent_views_added'):
        bot.add_view(ClaimView())
        bot.add_view(StartBuyingView())
        bot.add_view(BuyView())
        bot.add_view(ReceiveUIView(0, "", "", 0, ""))
        bot.persistent_views_added = True
        print("✅ Vistas persistentes registradas (ClaimView, StartBuyingView, BuyView, ReceiveUIView)")

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
    
    # NOTA: El envío del mensaje de tienda se debería hacer solo una vez o verificar si ya existe.
    # Para evitar spam en cada reinicio, puedes comentar esto si ya enviaste el mensaje.
    service_channel = bot.get_channel(SERVICE_CHANNEL_ID)
    if service_channel:
        # Verificar si el último mensaje es del bot para no spamear (opcional)
        # async for msg in service_channel.history(limit=1):
        #     if msg.author == bot.user:
        #         return 

        embed = discord.Embed(
            title="🎨 𝐎𝐱𝐜𝐲𝐒𝐡𝐨𝐩 𝐒𝐭𝐨𝐫𝐞",
            description=(
                "Click the button below to start your order.\n"
                "Fill in your **UI name** and **UIX price** in the form."
            ),
            color=0xFF69B4  # Rosa vibrante, más moderno que rojo puro
        )

        # Imagen grande primero
        embed.set_image(url=BANNER_URL_OXCY_V2)

        # Footer con ícono
        embed.set_footer(text="OxcyShop - UI Design Marketplace", icon_url=BANNER_URL_ICON_V2)
        embed.timestamp = discord.utils.utcnow()

        # Mantener el view con el botón
        view = StartBuyingView()
        await service_channel.send(embed=embed, view=view) # Comentado para evitar spam, descomentar si se necesita reenviar



# --------------------- COMANDO STAFF: !sendUI ---------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def sendUI(ctx, member: discord.Member = None):
    """Envía un archivo o link de UI al usuario mediante un botón de claim con embed profesional, logs y clave RAR"""
    if not member:
        await ctx.send("❌ Debes mencionar a un usuario o usar su ID para enviar la UI.")
        return

    await ctx.send(
        f"📤 {ctx.author.mention}, sube el **archivo de la UI** o **pega el enlace** ahora (60s)."
    )

    def check(m):
        return m.author == ctx.author and (m.attachments or m.content.strip())

    try:
        msg = await bot.wait_for("message", timeout=60, check=check)

        # Determinar qué se envía (archivo o link)
        content_to_send = None
        is_file = False
        attachment = None
        if msg.attachments:
            attachment = msg.attachments[0]
            MAX_SIZE = 8 * 1024 * 1024
            if attachment.size <= MAX_SIZE:
                content_to_send = await attachment.to_file()
                is_file = True
            else:
                content_to_send = attachment.url
        else:
            content_to_send = msg.content.strip()

        RAR_PASSWORD = "2315"  # Clave del RAR que quieres agregar

        # Vista con botón profesional
        class ClaimUI(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.claimed = False

            @discord.ui.button(label="🆓 Claim Approved UI", style=discord.ButtonStyle.green)
            async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != member.id:
                    await interaction.response.send_message(
                        "❌ Este botón no es para ti.", ephemeral=True
                    )
                    return

                if self.claimed:
                    await interaction.response.send_message(
                        "❌ Esta UI ya ha sido reclamada.", ephemeral=True
                    )
                    return

                try:
                    # Enviar la UI al usuario
                    if is_file:
                        await member.send(
                            f"✅ Tu UI aprobada ha sido entregada:\nClave RAR: `{RAR_PASSWORD}`",
                            file=content_to_send
                        )
                        ui_description = f"Archivo: {attachment.filename}"
                        preview_url = attachment.url if attachment.content_type.startswith("image/") else None
                    else:
                        await member.send(
                            f"✅ Tu UI aprobada ha sido entregada:\n{content_to_send}\nClave RAR: `{RAR_PASSWORD}`"
                        )
                        ui_description = f"Link: {content_to_send}"
                        preview_url = content_to_send if content_to_send.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')) else None

                    # Confirmación embed profesional
                    confirm_embed = discord.Embed(
                        title="🎨 UI Delivered Successfully!",
                        description=f"Hola {member.mention}, tu UI ha sido entregada correctamente ✅",
                        color=0x00FFD5
                    )
                    confirm_embed.add_field(name="UI entregada", value=ui_description, inline=False)
                    confirm_embed.add_field(name="Clave RAR", value=RAR_PASSWORD, inline=True)
                    confirm_embed.add_field(name="Enviado por", value=ctx.author.mention, inline=True)
                    confirm_embed.set_footer(text="OxcyShop • UI Delivery")
                    confirm_embed.timestamp = discord.utils.utcnow()
                    if preview_url:
                        confirm_embed.set_image(url=preview_url)

                    await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

                    logs_channel = bot.get_channel(FREE_UI_LOGS_ID)
                    if logs_channel:
                        log_embed = discord.Embed(
                            title="🆓 Free UI Claimed",
                            description=f"{member.mention} ({member.id}) reclamó la UI",
                            color=0x00FFD5
                        )
                        log_embed.add_field(name="UI entregada", value=ui_description, inline=False)
                        log_embed.add_field(name="Clave RAR", value=RAR_PASSWORD, inline=True)
                        log_embed.add_field(name="Enviado por", value=ctx.author.mention, inline=True)
                        log_embed.set_footer(text="OxcyShop • Free UI Logs")
                        log_embed.timestamp = discord.utils.utcnow()
                        if preview_url:
                            log_embed.set_image(url=preview_url)
                        await logs_channel.send(embed=log_embed)

                    self.claimed = True
                    button.disabled = True
                    await interaction.message.edit(view=self)

                except discord.Forbidden:
                    await interaction.response.send_message(
                        "❌ No puedo enviarte DM.", ephemeral=True
                    )
                    self.stop()  # Desactivar el botón

        # Enviar DM al usuario con el botón
        try:
            await member.send(
                "🎉 Tu UI ha sido aprobada! Haz clic en el botón para reclamarla:",
                view=ClaimUI()
            )
            await ctx.send(f"✅ Mensaje de claim enviado a {member.mention}.")
        except discord.Forbidden:
            await ctx.send(f"❌ No puedo enviar DM a {member.mention}.")

    except asyncio.TimeoutError:
        await ctx.send("⌛ Tiempo agotado. Comando cancelado.")
    except Exception as e:
        await ctx.send(f"❌ Error inesperado: {type(e).__name__} - {e}")


# Comando de prueba
@bot.command()
async def test(ctx):
    """Envía el embed de bienvenida usando tu perfil para pruebas"""
    embed = crear_embed(ctx.author)

    # Botones interactivos
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Catalog", url="https://discord.com/channels/1286045119715475527/1449082718393733150"))
    view.add_item(discord.ui.Button(label="Contact Us", url="https://discord.com/users/998836610516914236"))

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
    if not message.author.bot:
        last_coin_time = coin_cooldowns.get(user_id)
        if not last_coin_time or (current_time - last_coin_time).total_seconds() > 60:
            rand = random.random()
            if rand < 0.4:
                coins_earned = random.randint(1, 4)
            elif rand < 0.75:
                coins_earned = random.randint(5, 10)
            else:
                coins_earned = random.randint(10, 15)
            database.add_coins(user_id, coins_earned)
            coin_cooldowns[user_id] = current_time
            # print(f"User {message.author} earned {coins_earned} coins.")

    # --- SPAM TRACKER ---
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []

    # Filtrar mensajes antiguos fuera del rango
    spam_tracker[user_id] = [
        msg_time for msg_time in spam_tracker[user_id]
        if (current_time - msg_time).total_seconds() < SPAM_TIME_WINDOW
    ]
    spam_tracker[user_id].append(current_time)

    if len(spam_tracker[user_id]) > SPAM_THRESHOLD:
        spam_embed = discord.Embed(
            title="⚠️ SPAM DETECTED",
            description=f"{message.author.mention}, you are sending too many messages too quickly.",
            color=0xFF0000
        )
        spam_embed.add_field(
            name="⛔ Warning",
            value="Please slow down. Continued spam may result in sanctions or a ban.",
            inline=False
        )
        spam_embed.set_footer(text="OxcyShop - Server Security")
        spam_embed.timestamp = discord.utils.utcnow()
        try:
            warning_msg = await message.channel.send(embed=spam_embed)
            await asyncio.sleep(240)
            await warning_msg.delete()
        except:
            pass
        spam_tracker[user_id] = [current_time]

    # --- FREE UI CLAIMS ---
    if user_id in freeui_claims:
        pass

    # --- ORDERS ---
    if user_id in pending_orders:
        order_info = pending_orders[user_id]
        if message.channel.id == order_info["channel_id"]:
            await message.add_reaction("✅")
            waiting_embed = discord.Embed(
                title="⏳ Waiting for Confirmation",
                description="Your payment proof has been received. Please wait for confirmation.\n\n**This may take 1-2 days.**",
                color=0xFFA500
            )
            waiting_embed.set_footer(text="OxcyShop - Order Management")
            waiting_embed.timestamp = discord.utils.utcnow()
            await message.reply(embed=waiting_embed)

            logs_channel = bot.get_channel(LOGS_CHANNEL_ID)
            if logs_channel:
                log_embed = discord.Embed(
                    title="💳 PAYMENT PROOF RECEIVED",
                    description=f"User {message.author.mention} sent payment proof",
                    color=0xFF6B9D
                )
                log_embed.add_field(name="👤 Customer", value=f"{message.author.mention}", inline=True)
                log_embed.add_field(name="🆔 User ID", value=f"`{user_id}`", inline=True)
                log_embed.add_field(name="🎨 Product", value=f"**{order_info['order_data']['ui_name']}**", inline=True)
                log_embed.add_field(name="💰 Price", value=f"**{order_info['order_data']['price']}**", inline=True)
                log_embed.add_field(name="💳 UIX Price", value=f"**{order_info['order_data']['payment_method']}**", inline=True)
                log_embed.add_field(name="📝 Message Content", value=f"{message.content or 'Proof received (no text)'}", inline=False)
                log_embed.set_thumbnail(url=message.author.avatar.url)
                log_embed.set_footer(text="OxcyShop - Store Management")
                log_embed.timestamp = discord.utils.utcnow()
                await logs_channel.send(embed=log_embed)

                for attachment in message.attachments:
                    await logs_channel.send(f"📎 Attachment from {message.author.mention}: {attachment.url}")

            del pending_orders[user_id]

    # --- STAFF LOGS para CONFIRMACIONES ---
    if message.channel.id == LOGS_CHANNEL_ID and message.mentions:
        mentioned_user = message.mentions[0]
        if mentioned_user.id in user_channels:
            channel_id = user_channels[mentioned_user.id]
            try:
                user_channel = bot.get_channel(channel_id)
                if user_channel:
                    completion_embed = discord.Embed(
                        title="✅ ORDER CONFIRMED & READY",
                        description=f"Hello {mentioned_user.mention}! 🎉\n\nYour order has been confirmed and is ready!",
                        color=0x00FF00
                    )
                    completion_embed.add_field(
                        name="📦 Order Details",
                        value="**Status**: ✅ Confirmed\n**Ready to Deliver",
                        inline=False
                    )
                    completion_embed.add_field(
                        name="📝 Staff Message",
                        value=f"{message.content or 'Order confirmed'}",
                        inline=False
                    )
                    if message.attachments:
                        completion_embed.add_field(
                            name="📎 Attachments",
                            value="\n".join([f"[{att.filename}]({att.url})" for att in message.attachments]),
                            inline=False
                        )
                    completion_embed.set_footer(text="OxcyShop - Order Complete", icon_url=BANNER_URL_OXCY_V2)
                    completion_embed.timestamp = discord.utils.utcnow()
                    await user_channel.send(f"{mentioned_user.mention}", embed=completion_embed)
                    await message.add_reaction("✅")
                    del user_channels[mentioned_user.id]
            except Exception as e:
                print(f"Error sending order confirmation: {e}")

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

@bot.tree.command(name="guix", description="Sell a UI for coins (Staff Only)")
@discord.app_commands.describe(price="Price in coins", image="Preview image of the UI")
async def slash_guix(interaction: discord.Interaction, price: int, image: discord.Attachment):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        img_url = image.url

        embed = discord.Embed(
            title="👑 PREMIUM UI AVAILABLE",
            description=f"✨ Click **Buy UI** to purchase access.\n💰 Price: **{price} coins**",
            color=0xD4AF37
        )
        embed.set_image(url=img_url)
        embed.add_field(name="⭐ Premium Quality", value="Exclusive Design • Fast Delivery • Full Support", inline=False)
        embed.set_footer(text="OxcyShop • 👑 Premium Collection", icon_url=BANNER_URL_ICON_V2)
        embed.timestamp = discord.utils.utcnow()

        premium_ui_channel = bot.get_channel(PREMIUM_UI_CHANNEL_ID)
        if premium_ui_channel:
            sent_msg = await premium_ui_channel.send(embed=embed, view=BuyView())
            
            # Save Price to DB
            database.add_guix_listing(sent_msg.id, price)
            
            await interaction.followup.send(f"✅ UI Premium publicada por {price} coins en {premium_ui_channel.mention}")
        else:
            await interaction.followup.send("❌ Premium UI channel not found!")

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="sendmonedas", description="Envía monedas a otro usuario")
@discord.app_commands.describe(usuario="Usuario que recibe las monedas", cantidad="Cantidad de monedas")
async def slash_sendmonedas(interaction: discord.Interaction, usuario: discord.User, cantidad: int):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Solo el owner puede usar este comando.", ephemeral=True)
        return
    
    if cantidad <= 0:
        await interaction.response.send_message("❌ La cantidad debe ser mayor a 0.", ephemeral=True)
        return
    
    if usuario.bot:
        await interaction.response.send_message("❌ No puedes dar monedas a bots.", ephemeral=True)
        return
    
    database.add_coins(usuario.id, cantidad)
    
    embed = discord.Embed(
        title="💰 Monedas Recibidas",
        description=f"{usuario.mention} ha recibido **{cantidad}** monedas de {interaction.user.mention}",
        color=0xD4AF37
    )
    embed.add_field(name="💰 Nuevo balance", value=f"`{database.get_coins(usuario.id)}` monedas", inline=False)
    embed.set_footer(text="OxcyShop • Sistema de Monedas")
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
