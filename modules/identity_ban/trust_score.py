import discord
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from difflib import SequenceMatcher
from .identity_manager import IdentityManager

class TrustScoreCalculator:
    
    @staticmethod
    def calculate_account_age_score(user: discord.Member) -> int:
        """
        Calcula puntuación basada en antigüedad de la cuenta (0-25 puntos)
        Más vieja = más puntos (más confiable)
        """
        account_age = datetime.now(user.created_at.tzinfo) - user.created_at
        days = account_age.days
        
        if days > 730:
            return 25
        elif days > 365:
            return 20
        elif days > 180:
            return 15
        elif days > 90:
            return 10
        elif days > 30:
            return 5
        else:
            return 0
    
    @staticmethod
    def similarity_ratio(a: str, b: str) -> float:
        """Calcula similaridad entre dos strings (0-1)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    @staticmethod
    def calculate_name_similarity(username: str, banned_users: List[Dict]) -> Tuple[int, str]:
        """
        Detecta nombres similares (0-20 puntos)
        Si el nombre es similar a alguien baneado, resta puntos
        """
        penalty = 0
        suspicious_user = ""
        
        for ban in banned_users:
            banned_name = ban.get("User", "").lower()
            if not banned_name:
                continue
            
            similarity = TrustScoreCalculator.similarity_ratio(username, banned_name)
            
            if similarity > 0.85:
                penalty = 20
                suspicious_user = ban.get("User", "")
                break
            elif similarity > 0.70:
                penalty = 10
                suspicious_user = ban.get("User", "")
            elif similarity > 0.50 and penalty < 5:
                penalty = 5
                suspicious_user = ban.get("User", "")
        
        return (20 - penalty, suspicious_user)
    
    @staticmethod
    def calculate_avatar_similarity(member: discord.Member, banned_users: List[Dict]) -> int:
        """
        Detecta avatares similares (0-15 puntos)
        Si usa el mismo avatar que alguien baneado, resta puntos
        """
        if not member.avatar:
            return 15
        
        avatar_url = str(member.avatar.url)
        penalty = 0
        
        for ban in banned_users:
            if ban.get("AvatarHash", "") and avatar_url.endswith(ban.get("AvatarHash", "")):
                penalty = 15
                break
        
        return 15 - penalty
    
    @staticmethod
    def calculate_server_overlap_score(member: discord.Member, banned_users: List[Dict]) -> int:
        """
        Detecta si el usuario comparte servidores con baneados (0-15 puntos)
        """
        penalty = 0
        server_id = str(member.guild.id)
        
        for ban in banned_users:
            if ban.get("Servidor") == server_id:
                penalty = 10
                break
        
        return 15 - penalty
    
    @staticmethod
    def calculate_id_pattern_score(user_id: int, banned_users: List[Dict]) -> Tuple[int, str]:
        """
        Detecta patrones de IDs sospechosos (0-10 puntos)
        IDs secuenciales o muy similares podrían indicar alts
        """
        penalty = 0
        suspicious_id = ""
        
        for ban in banned_users:
            try:
                banned_id = int(ban.get("ID", 0))
                id_difference = abs(user_id - banned_id)
                
                if id_difference < 100:
                    penalty = 10
                    suspicious_id = ban.get("ID", "")
                    break
                elif id_difference < 1000:
                    penalty = 5
                    suspicious_id = ban.get("ID", "")
            except (ValueError, TypeError):
                pass
        
        return (10 - penalty, suspicious_id)
    
    @staticmethod
    def calculate_trust_score(member: discord.Member) -> Dict:
        """
        Calcula el Trust Score completo (0-100 puntos)
        Retorna un diccionario con detalles del análisis
        """
        banned_users = IdentityManager.read_all_bans()
        
        if not banned_users:
            return {
                "score": 100,
                "is_suspicious": False,
                "reasons": [],
                "matched_users": [],
                "recommendations": "✅ Sin registros de baneo. Usuario confiable."
            }
        
        account_age_score = TrustScoreCalculator.calculate_account_age_score(member)
        name_score, name_match = TrustScoreCalculator.calculate_name_similarity(member.name, banned_users)
        avatar_score = TrustScoreCalculator.calculate_avatar_similarity(member, banned_users)
        server_score = TrustScoreCalculator.calculate_server_overlap_score(member, banned_users)
        id_score, id_match = TrustScoreCalculator.calculate_id_pattern_score(member.id, banned_users)
        
        total_score = account_age_score + name_score + avatar_score + server_score + id_score
        
        reasons = []
        matched_users = []
        
        if name_score < 20:
            reasons.append(f"🔴 Nombre similar a usuario baneado: {name_match}")
            matched_users.append(name_match)
        
        if avatar_score < 15:
            reasons.append("🔴 Avatar similar a usuario baneado")
        
        if server_score < 15:
            reasons.append("🔴 Antecedentes en el mismo servidor")
        
        if id_score < 10:
            reasons.append(f"🟡 ID muy similar a: {id_match}")
            matched_users.append(id_match)
        
        if account_age_score < 5:
            reasons.append("🟡 Cuenta muy nueva (menos de 30 días)")
        
        recommendation = "✅ Sin sospechas"
        if total_score < 50:
            recommendation = "🔴 BAN RECOMENDADO - Posible Alt/Ban Evader"
        elif total_score < 70:
            recommendation = "🟠 KICK RECOMENDADO - Investigación necesaria"
        elif total_score < 85:
            recommendation = "🟡 MONITOREAR - Caución recomendada"
        
        return {
            "score": total_score,
            "is_suspicious": total_score < 70,
            "reasons": reasons,
            "matched_users": list(set(matched_users)),
            "recommendations": recommendation,
            "breakdown": {
                "account_age": account_age_score,
                "name_similarity": name_score,
                "avatar_similarity": avatar_score,
                "server_overlap": server_score,
                "id_pattern": id_score
            }
        }
