import discord
from discord.ext import commands
from discord import app_commands
from .identity_manager import IdentityManager
from .trust_score import TrustScoreCalculator

class IdentityBanCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="check_trust", description="Verifica el Trust Score de un usuario")
    @app_commands.describe(user="Usuario a verificar")
    async def check_trust(self, interaction: discord.Interaction, user: discord.User):
        """Comando para ver el Trust Score de un usuario"""
        await interaction.response.defer()
        
        try:
            member = await interaction.guild.fetch_member(user.id)
        except discord.NotFound:
            await interaction.followup.send("❌ Usuario no encontrado en este servidor", ephemeral=True)
            return
        
        trust_data = TrustScoreCalculator.calculate_trust_score(member)
        
        embed = discord.Embed(
            title="🔍 ANÁLISIS DE TRUST SCORE",
            description=f"Análisis de seguridad para {user.mention}",
            color=0x3498db
        )
        
        embed.add_field(name="👤 Usuario", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="📅 Cuenta Creada", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        
        score = trust_data["score"]
        if score >= 85:
            color_indicator = "🟢"
        elif score >= 70:
            color_indicator = "🟡"
        else:
            color_indicator = "🔴"
        
        embed.add_field(name="🎯 Trust Score", value=f"{color_indicator} **{score}/100**", inline=True)
        
        embed.add_field(
            name="📊 Desglose Detallado",
            value=(
                f"✓ Antigüedad de cuenta: {trust_data['breakdown']['account_age']}/25\n"
                f"✓ Similaridad de nombre: {trust_data['breakdown']['name_similarity']}/20\n"
                f"✓ Similaridad de avatar: {trust_data['breakdown']['avatar_similarity']}/15\n"
                f"✓ Overlap de servidor: {trust_data['breakdown']['server_overlap']}/15\n"
                f"✓ Patrón de ID: {trust_data['breakdown']['id_pattern']}/10"
            ),
            inline=False
        )
        
        if trust_data["reasons"]:
            embed.add_field(
                name="🚨 Banderas de Riesgo",
                value="\n".join(trust_data["reasons"]),
                inline=False
            )
        else:
            embed.add_field(name="✅ Estado", value="Sin banderas de riesgo detectadas", inline=False)
        
        embed.add_field(name="💡 Recomendación", value=trust_data["recommendations"], inline=False)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        embed.set_footer(text="Sistema de Identidad - Ban Trust Score")
        
        await interaction.followup.send(embed=embed, ephemeral=False)
    
    @app_commands.command(name="view_bans", description="Ver todos los banes registrados")
    async def view_bans(self, interaction: discord.Interaction):
        """Comando para ver el historial de banes"""
        await interaction.response.defer(ephemeral=True)
        
        bans = IdentityManager.read_all_bans()
        
        if not bans:
            await interaction.followup.send("✅ No hay banes registrados en el sistema", ephemeral=True)
            return
        
        pages = []
        for i, ban in enumerate(bans, 1):
            embed = discord.Embed(
                title=f"📋 Bán #{i} de {len(bans)}",
                color=0xFF0000
            )
            
            embed.add_field(name="👤 Usuario", value=ban.get("User", "N/A"), inline=False)
            embed.add_field(name="🆔 ID", value=f"`{ban.get('ID', 'N/A')}`", inline=True)
            embed.add_field(name="📅 Fecha", value=ban.get("Fecha", "N/A"), inline=True)
            embed.add_field(name="🏢 Servidor", value=f"`{ban.get('Servidor', 'N/A')}`", inline=False)
            embed.add_field(name="📝 Notas", value=ban.get("Notas", "Sin notas"), inline=False)
            embed.add_field(name="📜 Historial", value=ban.get("Historial", "Sin historial"), inline=False)
            
            embed.set_footer(text="Sistema de Identidad - Ban Trust Score")
            pages.append(embed)
        
        if len(pages) == 1:
            await interaction.followup.send(embed=pages[0], ephemeral=True)
        else:
            current_page = 0
            
            view = PaginationView(pages, interaction.user)
            message = await interaction.followup.send(embed=pages[0], view=view, ephemeral=True)
            view.message = message
    
    @app_commands.command(name="search_user", description="Buscar un usuario en los registros de baneo")
    @app_commands.describe(user_id="ID del usuario a buscar")
    async def search_user(self, interaction: discord.Interaction, user_id: str):
        """Busca un usuario específico en los registros"""
        await interaction.response.defer(ephemeral=True)
        
        ban = IdentityManager.get_user_history(user_id)
        
        if not ban:
            await interaction.followup.send(f"❌ No se encontró registro para ID `{user_id}`", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 INFORMACIÓN DEL USUARIO",
            color=0xFF0000
        )
        
        embed.add_field(name="👤 Usuario", value=ban.get("User", "N/A"), inline=False)
        embed.add_field(name="🆔 ID", value=f"`{ban.get('ID', 'N/A')}`", inline=True)
        embed.add_field(name="📅 Fecha de Baneo", value=ban.get("Fecha", "N/A"), inline=True)
        embed.add_field(name="🏢 Servidor", value=f"`{ban.get('Servidor', 'N/A')}`", inline=False)
        embed.add_field(name="📝 Notas", value=ban.get("Notas", "Sin notas"), inline=False)
        embed.add_field(name="📜 Historial", value=ban.get("Historial", "Sin historial"), inline=False)
        
        embed.set_footer(text="Sistema de Identidad - Ban Trust Score")
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class PaginationView(discord.ui.View):
    def __init__(self, pages, user):
        super().__init__(timeout=300)
        self.pages = pages
        self.current_page = 0
        self.user = user
        self.message = None
    
    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.defer()
            return
        
        self.current_page = (self.current_page - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    
    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.defer()
            return
        
        self.current_page = (self.current_page + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)


async def setup(bot):
    await bot.add_cog(IdentityBanCommands(bot))
