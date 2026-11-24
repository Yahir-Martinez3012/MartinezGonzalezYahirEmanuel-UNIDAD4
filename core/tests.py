from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from cuentas.models import Usuario
from vacantes.models import Vacante


class InfrastructureEndpointTests(TestCase):
    def test_health_is_live_and_does_not_require_database(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn('timestamp', response.json())

    def test_ready_checks_database_without_returning_details(self):
        response = self.client.get('/ready/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ready', 'database': 'available'})

    def test_infrastructure_endpoint_returns_only_safe_instance_metadata(self):
        with override_settings(ALLOWED_HOSTS=['testserver']):
            response = self.client.get('/api/infraestructura/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn('instance', response.json())
        self.assertNotIn('DATABASE_URL', response.json())
        self.assertNotIn('SECRET_KEY', response.json())


class InicioYEstadisticasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('poblar_demo', '--usuarios', verbosity=0)

    def test_inicio_muestra_vacantes_y_categorias(self):
        r = self.client.get(reverse('inicio'))
        self.assertContains(r, 'Vacantes recientes')
        self.assertContains(r, 'Desarrollador Web Junior')
        self.assertNotContains(r, 'Diseñador UX/UI')           # pendiente: no es pública
        self.assertNotContains(r, 'Operador de Producción')    # cerrada: no es pública

    def test_poblar_demo_es_idempotente(self):
        total = Vacante.objects.count()
        call_command('poblar_demo', '--usuarios', verbosity=0)
        self.assertEqual(Vacante.objects.count(), total)

    def test_estadisticas_solo_admin(self):
        url = reverse('estadisticas')
        self.assertEqual(self.client.get(url).status_code, 302)           # sin sesión: al login
        self.client.login(username='estudiante_demo', password='ConectaUTC2026!')
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username='empresa_demo', password='ConectaUTC2026!')
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username='admin_utc', password='ConectaUTC2026!')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Estadísticas generales')

    def test_cuentas_demo_empresas_sin_acceso_por_defecto(self):
        u = Usuario.objects.get(username='empresa_autopartes')
        self.assertFalse(u.has_usable_password())


class DemoNoPisaCambiosTests(TestCase):
    def test_segunda_ejecucion_conserva_perfil_y_contrasena(self):
        call_command('poblar_demo', '--usuarios', verbosity=0)
        from estudiantes.models import PerfilEstudiante
        perfil = PerfilEstudiante.objects.get(usuario__username='estudiante_demo')
        perfil.nombre_completo = 'Nombre Editado'
        perfil.save()
        usuario = Usuario.objects.get(username='estudiante_demo')
        usuario.set_password('OtraClave#2026')
        usuario.save()

        call_command('poblar_demo', '--usuarios', verbosity=0)          # nuevo despliegue
        perfil.refresh_from_db()
        self.assertEqual(perfil.nombre_completo, 'Nombre Editado')
        self.assertTrue(Usuario.objects.get(username='estudiante_demo').check_password('OtraClave#2026'))

        call_command('poblar_demo', '--usuarios', '--restablecer', verbosity=0)
        perfil.refresh_from_db()
        self.assertEqual(perfil.nombre_completo, 'Ana Martínez (demo)')
        self.assertTrue(Usuario.objects.get(username='estudiante_demo').check_password('ConectaUTC2026!'))
