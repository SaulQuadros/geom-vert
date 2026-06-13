"""Estaqueamento da curva vertical: cotas das estacas ao longo do greide.

Módulo *puro* (sem UI). Dada uma curva já calculada (simétrica ou assimétrica) e
a estaca de um ponto de referência (PCV, PIV ou PTV), gera a relação de estacas
do PCV ao PTV com a cota do greide em cada uma.

Convenção brasileira: estaca = 20 m, notação "inteira + fração" (ex.: 39 + 10,00).
Estacas inteiras a cada 20 m, intermediárias a cada `passo_interm` (10 m por
padrão); os pontos notáveis PCV, PIV e PTV entram sempre, mesmo em fração.

A curva (simétrica ou assimétrica) deve expor: ``L``, ``x_piv``, ``greide_em(x)``
e ``tangente_em(x)`` — interface comum às duas dataclasses do pacote.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

TAMANHO_ESTACA = 20.0  # metros por estaca (padrão brasileiro)


@dataclass
class LinhaEstaca:
    """Uma linha da tabela de estaqueamento."""

    estaca: str           # "n + f,ff"
    dist_abs: float       # distância absoluta no eixo (m)
    x: float              # distância a partir do PCV (m)
    cota_tangente: float  # cota da rampa tangente de referência (m)
    flecha: float         # cota_tangente − cota_greide (m)
    cota_greide: float    # cota do greide / curva (m)
    ponto: str            # "PCV" | "M (sob PIV)" | "F (sob PIV)" | "PTV" | "Inteira" | "Intermediária"


def _formatar_estaca(dist: float) -> str:
    """Formata distância (m) como estaca 'inteira + fração' (vírgula decimal)."""
    n = math.floor(round(dist, 6) / TAMANHO_ESTACA)
    frac = dist - TAMANHO_ESTACA * n
    return f"{n} + {frac:05.2f}".replace(".", ",")


def gerar_estaqueamento(
    resultado,
    ponto_ref: str = "PIV",
    est_inteira: int = 0,
    fracao: float = 0.0,
    passo_interm: float = 10.0,
) -> list[LinhaEstaca]:
    """Gera a tabela de estaqueamento da curva, do PCV ao PTV.

    Args:
        resultado: curva calculada (simétrica ou assimétrica) com a interface
            comum (``L``, ``x_piv``, ``greide_em``, ``tangente_em``).
        ponto_ref: ponto cuja estaca é conhecida — ``"PCV"``, ``"PIV"`` ou ``"PTV"``.
        est_inteira: número da estaca inteira do ponto de referência.
        fracao: fração em metros (0 ≤ fração < 20) do ponto de referência.
        passo_interm: intervalo das estacas intermediárias (m). 10 m por padrão.

    Returns:
        Lista de :class:`LinhaEstaca`, ordenada por distância.
    """
    L = resultado.L
    x_piv = resultado.x_piv
    dist_ref = TAMANHO_ESTACA * est_inteira + fracao

    dist_pcv = {
        "PCV": dist_ref,
        "PIV": dist_ref - x_piv,
        "PTV": dist_ref - L,
    }[ponto_ref]
    dist_piv = dist_pcv + x_piv
    dist_ptv = dist_pcv + L

    eps = 1e-6
    # chave arredondada -> (distância, rótulo forçado ou None)
    pontos: dict[float, tuple[float, str | None]] = {}

    def add(d: float, label: str | None = None) -> None:
        key = round(d, 3)
        if key not in pontos or label is not None:
            pontos[key] = (d, label)

    # grade de estacas (múltiplos de passo_interm) dentro de [PCV, PTV]
    k0 = math.ceil((dist_pcv - eps) / passo_interm)
    k1 = math.floor((dist_ptv + eps) / passo_interm)
    for k in range(k0, k1 + 1):
        add(k * passo_interm)

    # pontos notáveis (sempre presentes, com rótulo)
    label_piv = "F (sob PIV)" if hasattr(resultado, "l1") else "M (sob PIV)"
    add(dist_pcv, "PCV")
    add(dist_piv, label_piv)
    add(dist_ptv, "PTV")

    linhas: list[LinhaEstaca] = []
    for key in sorted(pontos):
        d, label = pontos[key]
        x = min(max(d - dist_pcv, 0.0), L)
        ct = resultado.tangente_em(x)
        cg = resultado.greide_em(x)
        if label is None:
            n_est = d / TAMANHO_ESTACA
            label = "Inteira" if abs(n_est - round(n_est)) < 1e-6 else "Intermediária"
        linhas.append(
            LinhaEstaca(
                estaca=_formatar_estaca(d),
                dist_abs=d,
                x=x,
                cota_tangente=ct,
                flecha=ct - cg,
                cota_greide=cg,
                ponto=label,
            )
        )
    return linhas
