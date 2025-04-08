import logging
from datetime import datetime
import os
import traceback

class AppLogger:
    def __init__(self):
        # Créer le dossier logs s'il n'existe pas
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Configurer le logger principal
        self.logger = logging.getLogger('app_logger')
        self.logger.setLevel(logging.INFO)
        
        # Créer un handler pour les fichiers
        log_file = f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Créer un handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Définir le format des logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Ajouter les handlers au logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_backend_call(self, endpoint, method, params=None):
        """Log les appels au backend"""
        message = f"Backend call - {method} {endpoint}"
        if params:
            message += f" - Params: {params}"
        self.logger.info(message)
    
    def log_embedding_request(self, text, success=True, error=None):
        """Log les demandes d'embeddings"""
        status = "success" if success else "failed"
        message = f"Embedding request - {status}"
        if error:
            error_details = self._format_error(error)
            message += f" - Error: {error_details}"
        self.logger.info(message)
    
    def log_openai_call(self, model, operation, success=True, error=None, prompt=None):
        """Log les appels à OpenAI"""
        status = "success" if success else "failed"
        message = f"OpenAI call - Model: {model} - Operation: {operation} - {status}"
        if prompt:
            message += f" - Prompt: {prompt}"
        if error:
            error_details = self._format_error(error)
            message += f" - Error: {error_details}"
        self.logger.info(message)
    
    def _format_error(self, error):
        """Formate les détails d'une erreur avec traceback"""
        if isinstance(error, Exception):
            error_type = type(error).__name__
            error_msg = str(error)
            tb = traceback.extract_tb(error.__traceback__)
            if tb:
                last_frame = tb[-1]
                file_name = os.path.basename(last_frame.filename)
                line_number = last_frame.lineno
                function_name = last_frame.name
                return f"{error_type}: {error_msg} in {file_name}:{line_number} ({function_name})"
            return f"{error_type}: {error_msg}"
        return str(error)

# Créer une instance globale du logger
app_logger = AppLogger() 