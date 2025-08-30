#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metamorph Trading Bot - Entrada Principal

Bot automatizado para trading de criptomoedas na Binance Spot
baseado em sinais do Telegram.

Autor: Metamorph Team
Versão: 1.0.0
Licença: MIT
"""

import asyncio
import os
import sys
from typing import Optional

from telegram_handler import TelegramClientHandler
from binance_handler import BinanceHandler
from logger import log_action
from dotenv import load_dotenv


def load_environment_variables() -> tuple[Optional[str], ...]:
    """Carrega e valida variáveis de ambiente.
    
    Returns:
        tuple: Variáveis de configuração carregadas
    """
    load_dotenv()
    
    telegram_api_id = os.getenv("TELEGRAM_API_ID")
    telegram_api_hash = os.getenv("TELEGRAM_API_HASH")
    telegram_phone = os.getenv("TELEGRAM_PHONE")
    telegram_group = os.getenv("TELEGRAM_GROUP")
    
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")
    
    simulation_mode = os.getenv("SIMULATION_MODE", "False").lower() == "true"
    
    return (
        telegram_api_id, telegram_api_hash, telegram_phone, telegram_group,
        binance_api_key, binance_api_secret, simulation_mode
    )


async def main() -> None:
    """Função principal do bot."""
    try:
        # Carregar configurações
        (
            telegram_api_id, telegram_api_hash, telegram_phone, telegram_group,
            binance_api_key, binance_api_secret, simulation_mode
        ) = load_environment_variables()
        
        # Validar configurações obrigatórias
        if not all([telegram_api_id, telegram_api_hash, telegram_phone, telegram_group]):
            log_action("ERRO: Configurações do Telegram incompletas no arquivo .env")
            return
            
        if not all([binance_api_key, binance_api_secret]):
            log_action("ERRO: Configurações da Binance incompletas no arquivo .env")
            return
        
        # Inicializar handlers
        binance = BinanceHandler(binance_api_key, binance_api_secret, simulation_mode)
        telegram = TelegramClientHandler(
            telegram_api_id,
            telegram_api_hash,
            telegram_phone,
            telegram_group,
            binance
        )

        mode_text = "SIMULAÇÃO" if simulation_mode else "PRODUÇÃO"
        log_action(f"Bot iniciado em modo {mode_text}, aguardando sinais...")
        
        # Executar bot
        await telegram.run()
        
    except KeyboardInterrupt:
        log_action("Bot interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        log_action(f"Erro crítico no bot: {e}")
    finally:
        log_action("Bot finalizado")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot parado pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)