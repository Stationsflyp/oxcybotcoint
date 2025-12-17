import discord
from discord.ext import commands
from datetime import datetime
from .identity_manager import IdentityManager
from .trust_score import TrustScoreCalculator

ALERT_CHANNEL_ID = 1448647845921161267
DATA_CHANNEL_ID = 1448647859363905619

class IdentityBanEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Se dispara cuando un usuario es baneado"""
        try:
            ban_entry = await guild.fetch_ban(user)
            reason = ban_entry.reason or "Sin razón especificada"
            
            history = f"Baneado del servidor {guild.name} (ID: {guild.id})"
            
            IdentityManager.save_ban(
                user_id=user.id,
                username=f"{user.name}#{user.discriminator}",
                server_id=guild.id,
                notes=reason,
                history=history
            )
            
            embed = discord.Embed(
                title="📌 NUEVO BAN REGISTRADO",
                description=f"Usuario baneado ha sido registrado en el sistema",
                color=0xFF0000
            )
            embed.add_field(name="👤 Usuario", value=f"{user.name}#{user.discriminator}", inline=False)
            embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
            embed.add_field(name="📅 Fecha", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="🏢 Servidor", value=f"{guild.name} (ID: `{guild.id}`)", inline=False)
            embed.add_field(name="📝 Razón del Ban", value=f"```{reason}```", inline=False)
            
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            
            embed.set_footer(text="Sistema de Identidad - Ban Trust Score")
            
            data_channel = self.bot.get_channel(DATA_CHANNEL_ID)
            if data_channel:
                try:
                    await data_channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending ban data to channel: {e}")
        
        except Exception as e:
            print(f"Error in on_member_ban: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Se dispara cuando un nuevo miembro se une al servidor"""
        try:
            trust_data = TrustScoreCalculator.calculate_trust_score(member)
            
            if trust_data["is_suspicious"]:
                alert_embed = discord.Embed(
                    title="⚠️ ALERTA DE SEGURIDAD - Posible Alt/Ban Evader",
                    description=f"Un usuario sospechoso se ha unido al servidor",
                    color=0xFF6B00
                )
                
                alert_embed.add_field(
                    name="👤 Usuario",
                    value=f"{member.mention}\n`{member.name}#{member.discriminator}`",
                    inline=False
                )
                alert_embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
                alert_embed.add_field(name="📅 Cuenta Creada", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
                alert_embed.add_field(
                    name="🎯 Trust Score",
                    value=f"**{trust_data['score']}/100**",
                    inline=True
                )
                alert_embed.add_field(
                    name="📊 Desglose",
                    value=(
                        f"• Antigüedad: {trust_data['breakdown']['account_age']}/25\n"
                        f"• Nombre: {trust_data['breakdown']['name_similarity']}/20\n"
                        f"• Avatar: {trust_data['breakdown']['avatar_similarity']}/15\n"
                        f"• Servidor: {trust_data['breakdown']['server_overlap']}/15\n"
                        f"• Patrón ID: {trust_data['breakdown']['id_pattern']}/10"
                    ),
                    inline=False
                )
                
                if trust_data["reasons"]:
                    alert_embed.add_field(
                        name="🚨 Razones de Sospecha",
                        value="\n".join(trust_data["reasons"]),
                        inline=False
                    )
                
                if trust_data["matched_users"]:
                    alert_embed.add_field(
                        name="⛔ Coincidencias",
                        value=f"```{', '.join(trust_data['matched_users'])}```",
                        inline=False
                    )
                
                alert_embed.add_field(
                    name="💡 Recomendación",
                    value=trust_data["recommendations"],
                    inline=False
                )
                
                if member.avatar:
                    alert_embed.set_thumbnail(url=member.avatar.url)
                
                alert_embed.set_footer(text="Sistema de Identidad - Ban Trust Score")
                
                alert_channel = self.bot.get_channel(ALERT_CHANNEL_ID)
                if alert_channel:
                    try:
                        await alert_channel.send(
                            embed=alert_embed
                        )
                    except Exception as e:
                        print(f"Error sending alert: {e}")
            
        except Exception as e:
            print(f"Error in on_member_join: {e}")

async def setup(bot):
    await bot.add_cog(IdentityBanEvents(bot))
