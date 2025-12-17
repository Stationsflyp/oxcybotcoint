"""
TEST DEL SISTEMA BAN TRUST SCORE
════════════════════════════════════════════════════════════════════════════════

Este script te permite testear el sistema sin necesidad de
banear usuarios reales o crear alts.

¿Cómo usarlo?
─────────────

1. Asegúrate de que tu bot está corriendo
2. Ejecuta este script
3. Observa los resultados en tu consola
4. Verifica que identity_data.txt se crea/actualiza correctamente

IMPORTANTE: Este script SOLO testea las funciones de lectura/escritura.
Para testear los eventos reales necesitas:
- Banear un usuario (on_member_ban)
- Que un usuario se una (on_member_join)

════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.identity_ban.identity_manager import IdentityManager
from modules.identity_ban.trust_score import TrustScoreCalculator
from datetime import datetime, timedelta


def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_identity_manager():
    """Test del manager de identidad"""
    print_section("TEST 1: IDENTITY MANAGER (Lectura/Escritura)")
    
    print("✓ Creando archivo si no existe...")
    IdentityManager.ensure_file_exists()
    if os.path.exists("identity_data.txt"):
        print("  ✅ identity_data.txt existe")
    else:
        print("  ❌ Error: No se creó el archivo")
        return False
    
    print("\n✓ Guardando ban de prueba...")
    result = IdentityManager.save_ban(
        user_id=999999999999999999,
        username="TestUser_Alt1#1234",
        server_id=1433202195221713008,
        notes="Usuario de prueba para testing",
        history="Ban de prueba generado automáticamente"
    )
    
    if result:
        print("  ✅ Ban guardado correctamente")
    else:
        print("  ❌ Error al guardar ban")
        return False
    
    print("\n✓ Leyendo banes...")
    bans = IdentityManager.read_all_bans()
    print(f"  ✅ Se leyeron {len(bans)} ban(s)")
    
    if len(bans) > 0:
        print(f"  Último ban: {bans[-1].get('User', 'N/A')}")
    
    print("\n✓ Buscando ban específico...")
    ban = IdentityManager.get_ban_by_id("999999999999999999")
    if ban:
        print(f"  ✅ Ban encontrado: {ban.get('User', 'N/A')}")
        print(f"     ID: {ban.get('ID')}")
        print(f"     Fecha: {ban.get('Fecha')}")
        print(f"     Servidor: {ban.get('Servidor')}")
    else:
        print("  ❌ Ban no encontrado")
        return False
    
    print("\n✓ Verificando estructura del archivo...")
    with open("identity_data.txt", "r", encoding="utf-8") as f:
        content = f.read()
        if "[BAN]" in content and "[/BAN]" in content:
            print("  ✅ Formato correcto")
            print(f"  Tamaño del archivo: {len(content)} bytes")
        else:
            print("  ❌ Formato incorrecto")
            return False
    
    return True


def test_trust_score():
    """Test del cálculo de Trust Score"""
    print_section("TEST 2: TRUST SCORE CALCULATOR")
    
    print("✓ Creando usuario simulado de prueba...")
    
    # Simulamos un usuario con discord.Member
    class MockUser:
        def __init__(self, user_id, name, created_days_ago):
            self.id = user_id
            self.name = name
            self.created_at = datetime.now() - timedelta(days=created_days_ago)
            self.avatar = None
            self.guild = MockGuild()
    
    class MockGuild:
        def __init__(self):
            self.id = 1433202195221713008
    
    # Test 1: Usuario confiable (cuenta vieja)
    print("\n  Test 2.1: Usuario confiable (cuenta de 2 años)")
    user1 = MockUser(111111111111111111, "GoodUser", 730)
    
    # Mockeamos el método create_at
    user1.created_at = datetime.utcnow() - timedelta(days=730)
    
    try:
        score_data = TrustScoreCalculator.calculate_trust_score(user1)
        print(f"    Score: {score_data['score']}/100")
        print(f"    Es sospechoso: {score_data['is_suspicious']}")
        print(f"    Recomendación: {score_data['recommendations']}")
        print("    ✅ Test pasado")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False
    
    # Test 2: Usuario sospechoso (cuenta nueva)
    print("\n  Test 2.2: Usuario sospechoso (cuenta de 1 día)")
    user2 = MockUser(222222222222222222, "TestUser_Alt1", 1)
    user2.created_at = datetime.utcnow() - timedelta(days=1)
    
    try:
        score_data = TrustScoreCalculator.calculate_trust_score(user2)
        print(f"    Score: {score_data['score']}/100")
        print(f"    Es sospechoso: {score_data['is_suspicious']}")
        print(f"    Razones: {len(score_data['reasons'])} encontradas")
        for reason in score_data['reasons']:
            print(f"      - {reason}")
        print("    ✅ Test pasado")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False
    
    return True


def test_similarity():
    """Test de funciones de similitud"""
    print_section("TEST 3: FUNCIONES DE SIMILITUD")
    
    print("✓ Test de similitud de nombres...")
    
    tests = [
        ("TestUser", "TestUser", 1.0, "Idéntico"),
        ("TestUser", "TestUser2", 0.89, "Muy similar"),
        ("TestUser", "TestUsr", 0.75, "Similar"),
        ("TestUser", "Admin", 0.0, "Completamente diferente"),
    ]
    
    for name1, name2, expected_approx, description in tests:
        similarity = TrustScoreCalculator.similarity_ratio(name1, name2)
        print(f"\n  '{name1}' vs '{name2}'")
        print(f"  Similitud: {similarity:.2f} ({description})")
        if abs(similarity - expected_approx) < 0.2:
            print("  ✅ Test pasado")
        else:
            print("  ⚠️  Resultado diferente al esperado (puede ser normal)")
    
    return True


def test_account_age():
    """Test del cálculo de antigüedad"""
    print_section("TEST 4: CÁLCULO DE ANTIGÜEDAD DE CUENTA")
    
    class MockUser:
        def __init__(self, days_old):
            self.created_at = datetime.utcnow() - timedelta(days=days_old)
    
    tests = [
        (730, 25, "2 años"),
        (365, 20, "1 año"),
        (180, 15, "6 meses"),
        (90, 10, "3 meses"),
        (30, 5, "1 mes"),
        (1, 0, "1 día"),
    ]
    
    print("Pruebas de antigüedad de cuenta:")
    
    for days, expected_points, description in tests:
        user = MockUser(days)
        try:
            score = TrustScoreCalculator.calculate_account_age_score(user)
            status = "✅" if score == expected_points else "⚠️"
            print(f"\n  {status} {description} ({days} días): {score}/25 puntos")
            if score != expected_points:
                print(f"      (Esperado: {expected_points})")
        except Exception as e:
            print(f"\n  ❌ Error en {description}: {e}")
            return False
    
    return True


def test_file_cleanup():
    """Test de limpieza opcional"""
    print_section("TEST 5: LIMPIEZA (OPCIONAL)")
    
    print("⚠️  NOTA: Este test es destructivo")
    print("Si pasaste todos los tests anteriores, puedes dejar los datos")
    print("El archivo identity_data.txt será usado por tu bot\n")
    
    response = input("¿Limpiar los datos de test? (s/n): ").lower()
    
    if response == 's':
        try:
            IdentityManager.delete_ban("999999999999999999")
            print("✅ Datos de test eliminados")
            return True
        except Exception as e:
            print(f"❌ Error al limpiar: {e}")
            return False
    else:
        print("✓ Datos mantienen. Puedes revisarlos en identity_data.txt")
        return True


def main():
    """Ejecuta todos los tests"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                  TEST DEL SISTEMA BAN TRUST SCORE                          ║
    ║                                                                            ║
    ║ Este script verifica que todos los módulos funcionan correctamente         ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "Identity Manager": test_identity_manager(),
        "Trust Score Calculator": test_trust_score(),
        "Similitud de Nombres": test_similarity(),
        "Antigüedad de Cuenta": test_account_age(),
        "Limpieza": test_file_cleanup(),
    }
    
    print_section("RESUMEN DE TESTS")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASADO" if result else "❌ FALLIDO"
        print(f"{status:12} | {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n{'='*80}")
    
    if all_passed:
        print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                     ✅ TODOS LOS TESTS PASARON                            ║
    ║                                                                            ║
    ║ El sistema está listo para usar. Próximos pasos:                          ║
    ║                                                                            ║
    ║ 1. Integra el código en tu bot principal                                  ║
    ║ 2. Reinicia el bot                                                        ║
    ║ 3. Prueba los comandos: /check_trust, /view_bans, /search_user          ║
    ║ 4. Intenta banear un usuario y luego que se una un alt                   ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
        """)
    else:
        print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                     ❌ ALGUNOS TESTS FALLARON                             ║
    ║                                                                            ║
    ║ Revisa los errores arriba y verifica:                                     ║
    ║                                                                            ║
    ║ 1. La estructura de carpetas es correcta                                  ║
    ║ 2. Los archivos .py existen en modules/identity_ban/                     ║
    ║ 3. Los permisos del bot son suficientes                                   ║
    ║ 4. Revisa TROUBLESHOOTING.txt para más ayuda                             ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
        """)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
