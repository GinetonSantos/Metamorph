# tax_reporter.py
import csv
import os
from datetime import datetime
from typing import Dict, List

class TaxReporter:
    """Sistema de registro de operações para declaração de IR"""
    
    def __init__(self, filename="operacoes_ir.csv"):
        self.filename = filename
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Cria arquivo CSV se não existir"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Data/Hora',
                    'Tipo Operação',
                    'Par',
                    'Quantidade',
                    'Preço Unitário',
                    'Valor Total (USDT)',
                    'Taxa (USDT)',
                    'Valor Líquido (USDT)',
                    'ID Sinal',
                    'Status',
                    'Observações'
                ])
    
    def register_buy_operation(self, symbol: str, quantity: float, price: float, 
                             total_value: float, fee: float, signal_id: str):
        """Registra operação de compra"""
        self._write_operation(
            tipo='COMPRA',
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_value=total_value,
            fee=fee,
            signal_id=signal_id,
            status='EXECUTADA',
            obs=f'Compra automática via bot - Sinal {signal_id}'
        )
    
    def register_sell_operation(self, symbol: str, quantity: float, price: float,
                              total_value: float, fee: float, signal_id: str, 
                              sell_type: str = 'TAKE_PROFIT'):
        """Registra operação de venda"""
        obs_map = {
            'TAKE_PROFIT': 'Venda automática - Take Profit',
            'STOP_LOSS': 'Venda automática - Stop Loss',
            'MANUAL': 'Venda manual'
        }
        
        self._write_operation(
            tipo='VENDA',
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_value=total_value,
            fee=fee,
            signal_id=signal_id,
            status='EXECUTADA',
            obs=obs_map.get(sell_type, 'Venda automática')
        )
    
    def register_failed_operation(self, symbol: str, signal_id: str, reason: str):
        """Registra operação que falhou"""
        self._write_operation(
            tipo='FALHA',
            symbol=symbol,
            quantity=0,
            price=0,
            total_value=0,
            fee=0,
            signal_id=signal_id,
            status='FALHOU',
            obs=f'Operação não executada: {reason}'
        )
    
    def _write_operation(self, tipo: str, symbol: str, quantity: float, price: float,
                        total_value: float, fee: float, signal_id: str, 
                        status: str, obs: str):
        """Escreve operação no CSV"""
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    tipo,
                    symbol,
                    f"{quantity:.8f}".rstrip('0').rstrip('.'),
                    f"{price:.8f}".rstrip('0').rstrip('.'),
                    f"{total_value:.2f}",
                    f"{fee:.8f}".rstrip('0').rstrip('.'),
                    f"{total_value - fee:.2f}",
                    signal_id,
                    status,
                    obs
                ])
        except Exception as e:
            print(f"Erro ao registrar operação: {e}")
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Gera resumo mensal para IR"""
        try:
            operations = []
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    op_date = datetime.strptime(row['Data/Hora'], '%d/%m/%Y %H:%M:%S')
                    if op_date.year == year and op_date.month == month:
                        operations.append(row)
            
            summary = {
                'total_compras': 0,
                'total_vendas': 0,
                'total_taxas': 0,
                'operacoes_executadas': 0,
                'operacoes_falhadas': 0
            }
            
            for op in operations:
                if op['Status'] == 'EXECUTADA':
                    summary['operacoes_executadas'] += 1
                    summary['total_taxas'] += float(op['Taxa (USDT)'])
                    
                    if op['Tipo Operação'] == 'COMPRA':
                        summary['total_compras'] += float(op['Valor Total (USDT)'])
                    elif op['Tipo Operação'] == 'VENDA':
                        summary['total_vendas'] += float(op['Valor Total (USDT)'])
                else:
                    summary['operacoes_falhadas'] += 1
            
            return summary
            
        except Exception as e:
            print(f"Erro ao gerar resumo: {e}")
            return {}