import os
import json
from datetime import datetime
from typing import Dict, List, Optional

IDENTITY_FILE = "identity_data.txt"

class IdentityManager:
    
    @staticmethod
    def ensure_file_exists():
        """Crea el archivo si no existe"""
        if not os.path.exists(IDENTITY_FILE):
            with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
                f.write("")
    
    @staticmethod
    def parse_ban_entry(entry: str) -> Optional[Dict]:
        """Parsea un bloque [BAN]...[/BAN] a un diccionario"""
        if not entry.strip().startswith("[BAN]") or not entry.strip().endswith("[/BAN]"):
            return None
        
        data = {}
        lines = entry.strip().split("\n")[1:-1]
        
        for line in lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        
        return data if data else None
    
    @staticmethod
    def read_all_bans() -> List[Dict]:
        """Lee todos los registros de banes del archivo"""
        IdentityManager.ensure_file_exists()
        
        try:
            with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading identity file: {e}")
            return []
        
        bans = []
        entries = content.split("[BAN]")
        
        for entry in entries[1:]:
            if "[/BAN]" in entry:
                ban_data = IdentityManager.parse_ban_entry("[BAN]" + entry)
                if ban_data:
                    bans.append(ban_data)
        
        return bans
    
    @staticmethod
    def get_ban_by_id(user_id: str) -> Optional[Dict]:
        """Obtiene un baneo específico por ID"""
        bans = IdentityManager.read_all_bans()
        for ban in bans:
            if ban.get("ID") == user_id:
                return ban
        return None
    
    @staticmethod
    def save_ban(user_id: int, username: str, server_id: int, notes: str = "", 
                 history: str = "") -> bool:
        """Guarda un nuevo baneo en el archivo"""
        IdentityManager.ensure_file_exists()
        
        try:
            ban_block = f"""[BAN]
ID: {user_id}
User: {username}
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Servidor: {server_id}
Historial: {history if history else "Sin historial previo"}
Notas: {notes if notes else "Sin notas"}
[/BAN]
"""
            
            with open(IDENTITY_FILE, "a", encoding="utf-8") as f:
                f.write(ban_block)
            
            return True
        except Exception as e:
            print(f"Error saving ban: {e}")
            return False
    
    @staticmethod
    def get_user_history(user_id: str) -> Optional[Dict]:
        """Obtiene el historial completo de un usuario"""
        return IdentityManager.get_ban_by_id(user_id)
    
    @staticmethod
    def delete_ban(user_id: str) -> bool:
        """Elimina un baneo del archivo (por ID de usuario)"""
        IdentityManager.ensure_file_exists()
        
        try:
            with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            
            bans = IdentityManager.read_all_bans()
            remaining_bans = [b for b in bans if b.get("ID") != user_id]
            
            new_content = ""
            for ban in remaining_bans:
                new_content += f"""[BAN]
ID: {ban.get('ID')}
User: {ban.get('User')}
Fecha: {ban.get('Fecha')}
Servidor: {ban.get('Servidor')}
Historial: {ban.get('Historial')}
Notas: {ban.get('Notas')}
[/BAN]
"""
            
            with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return True
        except Exception as e:
            print(f"Error deleting ban: {e}")
            return False
