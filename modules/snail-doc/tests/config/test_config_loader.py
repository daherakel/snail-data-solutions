"""
Tests para el sistema de configuración
"""

import unittest
import os
import tempfile
import yaml
from pathlib import Path


class TestConfigLoader(unittest.TestCase):
    """Tests para el config loader."""
    
    def setUp(self):
        """Configurar para cada test."""
        self.test_config = {
            'default': {
                'tenant_id': 'default',
                'tenant_name': 'Default Tenant',
                'agent': {
                    'personality': 'warm'
                }
            }
        }
    
    def test_tenant_config_structure(self):
        """Test de estructura de configuración de tenant."""
        self.assertIn('default', self.test_config)
        self.assertIn('tenant_id', self.test_config['default'])
        self.assertIn('agent', self.test_config['default'])
    
    def test_agent_personality_options(self):
        """Test de opciones de personalidad."""
        valid_personalities = ['warm', 'professional', 'technical', 'friendly']
        personality = self.test_config['default']['agent']['personality']
        self.assertIn(personality, valid_personalities)


if __name__ == '__main__':
    unittest.main()

