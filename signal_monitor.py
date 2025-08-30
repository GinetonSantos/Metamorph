# signal_monitor.py
import threading
from datetime import datetime

class SignalMonitor:
    """Sistema de comunicação entre bot e GUI"""
    
    def __init__(self):
        self.gui_callback = None
        self.lock = threading.Lock()
    
    def set_gui_callback(self, callback):
        """Define callback da GUI para receber atualizações"""
        with self.lock:
            self.gui_callback = callback
    
    def signal_received(self, symbol, signal_id):
        """Notifica que um sinal foi recebido"""
        self._notify_gui(symbol, f"Sinal recebido: {signal_id}", "info")
    
    def operation_success(self, symbol, operation_type, details=""):
        """Notifica operação bem-sucedida"""
        self._notify_gui(symbol, f"{operation_type} executada com sucesso {details}", "success")
    
    def operation_failed(self, symbol, reason):
        """Notifica falha na operação"""
        self._notify_gui(symbol, f"Operação falhou: {reason}", "error")
    
    def insufficient_balance(self, symbol, required, available):
        """Notifica saldo insuficiente"""
        self._notify_gui(symbol, f"Saldo insuficiente: {available:.2f} < {required:.2f} USDT", "warning")
    
    def _notify_gui(self, symbol, message, status_type):
        """Envia notificação para GUI de forma thread-safe"""
        with self.lock:
            if self.gui_callback:
                try:
                    self.gui_callback(symbol, message, status_type)
                except Exception as e:
                    print(f"Erro ao notificar GUI: {e}")

# Instância global para comunicação
signal_monitor = SignalMonitor()