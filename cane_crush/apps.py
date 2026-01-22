from django.apps import AppConfig


class CaneCrushConfig(AppConfig):
    name = 'cane_crush'
    
    def ready(self):
        """Import signals when app is ready"""
        import cane_crush.signals