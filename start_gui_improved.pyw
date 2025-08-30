#!/usr/bin/env python3
# start_gui_improved.pyw
"""
Interface Gráfica Melhorada do Metamorph Trading Bot - SEM CONSOLE
Funcionalidades:
- Controle inteligente de botões
- Monitor de sinais em tempo real
- Registro automático para IR
- Logs em janela separada
- Conversão USD automática
- Console oculto no Windows
"""

import sys
import os

# Ocultar console no Windows
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

if __name__ == "__main__":
    from gui_improved import TradingBotGUI
    
    try:
        app = TradingBotGUI()
        app.run()
    except Exception as e:
        # Em caso de erro, mostrar em messagebox
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Ocultar janela principal
        messagebox.showerror("Erro", f"Erro ao iniciar aplicação:\n{e}")
        root.destroy()