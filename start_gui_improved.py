#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metamorph Trading Bot - Interface Gráfica

Interface gráfica melhorada com funcionalidades avançadas:
- Controle inteligente de botões
- Monitor de sinais em tempo real
- Registro automático para IR
- Logs em janela separada
- Conversão USD automática

Autor: Metamorph Team
Versão: 1.0.0
Licença: MIT
"""

import sys


def main() -> None:
    """Função principal da interface gráfica."""
    try:
        from gui_improved import TradingBotGUI
        
        print("Iniciando Metamorph Trading Bot - Interface Melhorada...")
        app = TradingBotGUI()
        app.run()
        
    except ImportError as e:
        print(f"Erro: Módulos necessários não encontrados: {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()