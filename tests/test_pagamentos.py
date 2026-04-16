import pytest
from app.pagamentos import (
    calcular_desconto,
    aplicar_juros_atraso,
    validar_metodo_pagamento,
    processar_reembolso
)


def test_calcular_desconto():
    # Arrange
    valor = 100
    percentual = 10

    # Act
    resultado = calcular_desconto(valor, percentual)

    # Assert
    assert resultado == 90


def test_aplicar_juros_atraso():
    # Arrange
    valor_pago = 100
    dias_atraso = 5
    dias_ok = 0

    # Act
    resultado_com_atraso = aplicar_juros_atraso(valor_pago, dias_atraso)
    resultado_sem_atraso = aplicar_juros_atraso(valor_pago, dias_ok)

    # Assert
    # Juros simples de 1% ao dia: 100 + (100 * 0.01 * 5) = 105.0
    assert resultado_com_atraso == 105.0
    assert resultado_sem_atraso == 100.0


def test_validar_metodo_pagamento():
    # Arrange
    metodos_aceitos = ["pix", "cartao_credito", "cartao_debito", "boleto"]
    metodos_rejeitados = ["cheque", "dinheiro", "transferencia", "cripto"]

    # Act
    resultados_aceitos = [validar_metodo_pagamento(m) for m in metodos_aceitos]
    resultados_rejeitados = [validar_metodo_pagamento(m) for m in metodos_rejeitados]

    # Assert
    assert all(resultados_aceitos), "Todos os metodos validos devem ser aceitos"
    assert not any(resultados_rejeitados), "Nenhum metodo invalido deve ser aceito"


def test_validar_metodo_pagamento_case_insensitive():
    # Arrange
    metodo_maiusculo = "PIX"
    metodo_misto = "Cartao_Credito"

    # Act
    resultado_maiusculo = validar_metodo_pagamento(metodo_maiusculo)
    resultado_misto = validar_metodo_pagamento(metodo_misto)

    # Assert
    assert resultado_maiusculo is True
    assert resultado_misto is True


def test_processar_reembolso():
    # Arrange
    valor_pago = 357.89
    valor_reembolso_parcial = 123.45
    valor_reembolso_invalido = 500.00

    # Act
    resultado_parcial = processar_reembolso(valor_pago, valor_reembolso_parcial)
    resultado_invalido = processar_reembolso(valor_pago, valor_reembolso_invalido)

    # Assert
    assert round(resultado_parcial, 2) == round(valor_pago - valor_reembolso_parcial, 2)
    assert resultado_invalido == -1


def test_processar_reembolso_valor_exato():
    # Arrange
    valor_pago = 200.00
    valor_reembolso = 200.00  # Caso de Valor Limite

    # Act
    resultado = processar_reembolso(valor_pago, valor_reembolso)

    # Assert
    assert resultado == 0.00  # Caso de Valor Limite


def test_processar_reembolso_estouro_fronteira():
    # Arrange
    valor_pago = 200.00
    valor_reembolso = 201.00  # Caso de Valor Limite

    # Act
    resultado = processar_reembolso(valor_pago, valor_reembolso)

    # Assert
    assert resultado == -1  # Caso de Valor Limite