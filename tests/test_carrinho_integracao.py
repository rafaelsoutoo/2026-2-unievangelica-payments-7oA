#!/usr/bin/env python3
"""
Testes de INTEGRAÇÃO — Módulo Carrinho (SQLite :memory:)
Aula 11 — Teste de Software (2026.1) | UniCode UniEvangelica

=======================================================================
⚠️  POR QUE ESTE ARQUIVO É DIFERENTE DE test_pagamentos.py?
=======================================================================

  test_pagamentos.py       →  TESTE UNITÁRIO
  ─────────────────────       ─────────────────────────────────────────
  • Testa funções puras       • Sem banco de dados real
  • Usa Stubs/Mocks            • Sem rede, sem arquivo externo
  • Rápido: < 1ms por teste   • Isola a LÓGICA de negócio

  test_carrinho_integracao.py →  TESTE DE INTEGRAÇÃO
  ────────────────────────────   ──────────────────────────────────────
  • Testa módulo + banco real  • SQLite real (em memória)
  • Sem Mocks — toca o banco!  • Verifica PERSISTÊNCIA dos dados
  • Um pouco mais lento        • Isola via fixture (banco novo p/ cada teste)

=======================================================================
"""

import sqlite3
import pytest
import sys
import os

# Garante que o pacote 'app' é encontrado independente de onde o aluno rodar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.carrinho_db import (
    criar_tabela,
    adicionar_item,
    listar_itens,
    calcular_total,
    limpar_carrinho,
)


# =====================================================================
# FIXTURE — Banco de dados isolado por teste
# =====================================================================

@pytest.fixture
def db():
    """
    Fixture que entrega uma conexão SQLite ':memory:' com a tabela
    'carrinho' já criada.

    O banco EM MEMÓRIA é:
      ✅ Criado do zero antes de cada teste (setup)
      ✅ Destruído automaticamente ao fim de cada teste (teardown)
      ✅ Completamente isolado — um teste não suja o outro
    """
    conn = sqlite3.connect(":memory:")   # banco vive apenas na RAM
    criar_tabela(conn)                   # cria a estrutura da tabela
    yield conn                           # entrega para o teste
    conn.close()                         # teardown: banco destruído aqui


# =====================================================================
# GRUPO 1 — Testes de Inserção e Persistência
# =====================================================================

def test_item_persiste_no_banco(db):
    """
    Verifica que um item inserido realmente fica no banco
    com os dados corretos.
    """
    # Arrange: insere um item no banco
    adicionar_item(db, "Notebook", 3500.00, 1)

    # Act: recupera os itens persistidos
    itens = listar_itens(db)

    # Assert: o item está lá e os dados batem com o que foi inserido
    assert len(itens) == 1
    assert itens[0]["nome"] == "Notebook"
    assert itens[0]["preco"] == 3500.00
    assert itens[0]["quantidade"] == 1


def test_multiplos_itens_persistem(db):
    """
    Verifica que três itens distintos são persistidos corretamente.
    """
    # Arrange: insere 3 itens distintos
    adicionar_item(db, "Mouse", 150.00, 1)
    adicionar_item(db, "Teclado", 300.00, 2)
    adicionar_item(db, "Monitor", 1200.00, 1)

    # Act: lista todos os itens
    itens = listar_itens(db)

    # Assert: exatamente 3 itens retornados
    assert len(itens) == 3


def test_preco_negativo_lanca_value_error(db):
    """
    Verifica que passar preço negativo levanta ValueError
    antes de qualquer escrita no banco.
    """
    # Arrange + Act + Assert: a função deve lançar ValueError
    with pytest.raises(ValueError):
        adicionar_item(db, "Produto Inválido", -10.00, 1)


# =====================================================================
# GRUPO 2 — Testes de Cálculo de Total
# =====================================================================

def test_carrinho_vazio_retorna_zero(db):
    """
    Verifica que o total de um carrinho sem itens é 0.0.
    """
    # Arrange: banco vazio — nenhum insert

    # Act + Assert: calcular_total deve retornar 0.0
    assert calcular_total(db) == 0.0


def test_total_considera_quantidade(db):
    """
    Verifica que o total multiplica preço pela quantidade.
    """
    # Arrange: insere 3 unidades de R$ 50,00
    adicionar_item(db, "Caneta", 50.00, 3)

    # Act: calcula o total
    total = calcular_total(db)

    # Assert: 50.00 x 3 = 150.0
    assert total == 150.0


def test_total_multiplos_itens(db):
    """
    Verifica que o total soma corretamente itens com
    preços e quantidades diferentes.
    """
    # Arrange: 3 itens com preços e quantidades variados
    adicionar_item(db, "Item A", 10.00, 2)   # 20.00
    adicionar_item(db, "Item B", 25.00, 3)   # 75.00
    adicionar_item(db, "Item C", 100.00, 1)  # 100.00

    # Act: calcula o total
    total = calcular_total(db)

    # Assert: 20.00 + 75.00 + 100.00 = 195.00
    assert total == 195.0


# =====================================================================
# GRUPO 3 — Testes de Limpeza do Carrinho
# =====================================================================

def test_limpar_remove_todos_os_itens(db):
    """
    Verifica que limpar_carrinho remove todos os itens
    e zera o total.
    """
    # Arrange: adiciona 2 itens
    adicionar_item(db, "Produto X", 80.00, 1)
    adicionar_item(db, "Produto Y", 120.00, 2)

    # Act: limpa o carrinho
    limpar_carrinho(db)

    # Assert: lista vazia e total zerado
    assert listar_itens(db) == []
    assert calcular_total(db) == 0.0


def test_pode_adicionar_apos_limpar(db):
    """
    Verifica que o carrinho aceita novos itens normalmente
    após ser limpo, e que apenas o novo item existe.
    """
    # Arrange: adiciona um item e limpa
    adicionar_item(db, "Item Antigo", 500.00, 1)
    limpar_carrinho(db)

    # Act: adiciona um novo item após a limpeza
    adicionar_item(db, "Item Novo", 99.00, 1)
    itens = listar_itens(db)

    # Assert: somente o item novo existe no banco
    assert len(itens) == 1
    assert itens[0]["nome"] == "Item Novo"
    assert itens[0]["preco"] == 99.00