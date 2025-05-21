"""
Gerenciador de templates para currículos
Este módulo fornece uma classe para gerenciar diferentes templates de currículo.
"""
import os
import glob
import importlib.util

class TemplateManager:
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        self.available_templates = self._discover_templates()
    
    def _discover_templates(self):
        """Descobre todos os templates disponíveis na pasta de templates"""
        templates = {}
        
        # Verificar se a pasta de templates existe
        if not os.path.exists(self.template_dir):
            print(f"Pasta de templates '{self.template_dir}' não encontrada.")
            return templates
        
        # Encontrar todos os arquivos de template
        template_files = glob.glob(os.path.join(self.template_dir, 'template_*.py'))
        
        for template_file in template_files:
            # Extrair nome do template (template_xxx.py -> xxx)
            file_name = os.path.basename(template_file)
            template_name = file_name.replace('template_', '').replace('.py', '')
            
            templates[template_name] = {
                'name': template_name,
                'file': template_file
            }
        
        return templates
    
    def get_template(self, template_name):
        """Carrega um template específico pelo nome"""
        if template_name not in self.available_templates:
            raise ValueError(f"Template '{template_name}' não encontrado.")
            
        template_file = self.available_templates[template_name]['file']
        
        # Carregar dinamicamente o módulo de template
        spec = importlib.util.spec_from_file_location(f"template_{template_name}", template_file)
        template_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_module)
        
        return template_module
    
    def list_templates(self):
        """Lista todos os templates disponíveis"""
        return list(self.available_templates.keys())
