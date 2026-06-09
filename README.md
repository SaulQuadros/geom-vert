# Projeto Geométrico de Vias — Instrumento Didático

Ferramenta interativa de apoio à disciplina de **Projeto Geométrico de Vias**.
O primeiro módulo cobre a **concordância vertical** (curva vertical parabólica),
nos modos **simétrico** (PIV no meio, x = L/2) e **assimétrico** (dois trechos
com l₁ ≠ l₂), selecionáveis por um toggle no sidebar: cálculo dos pontos notáveis
(PCV, PTV, PIV e vértice), flecha, desnível e desenho do perfil longitudinal.
Inclui **estaqueamento** (estaca = 20 m): a partir da estaca de um ponto de
referência (PIV, PCV ou PTV), gera as cotas do greide nas estacas inteiras (20 m)
e intermediárias (10 m), com download em CSV.

A lógica de cálculo e de desenho fica em um **núcleo único e puro** (`geom_vert/`),
reaproveitado por duas interfaces:

- **Web (Streamlit)** — interface principal, acessada por link, sem instalação.
- **Desktop (Tkinter)** — base para um executável local (`.exe`), uso offline.

## Estrutura

```
geom_vert/
├── geom_vert/                    # núcleo (cálculo + plotagem), sem dependência de UI
│   ├── concordancia_vertical.py             # curva simétrica
│   ├── concordancia_vertical_assimetrica.py # curva assimétrica (l₁ ≠ l₂)
│   ├── estaqueamento.py                      # gerar_estaqueamento() (cotas das estacas)
│   └── plotagem.py               # plotar_perfil() / plotar_perfil_assimetrica()
├── app.py                        # Streamlit: página inicial
├── pages/1_Concordancia_Vertical.py   # Streamlit: módulo (expansão = novo arquivo aqui)
├── desktop/desktop.py            # Tkinter (base do .exe)
├── notebooks/                    # notebook original (referência didática)
├── z_docs/                       # PDFs do curso
└── requirements.txt
```

## Rodar localmente (web)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre no navegador (normalmente http://localhost:8501).

## Publicar na web (Streamlit Community Cloud — gratuito)

1. Suba esta pasta para um repositório no GitHub (público **ou** privado).
2. Acesse https://share.streamlit.io e conecte a conta do GitHub.
3. Escolha o repositório, branch e o arquivo principal **`app.py`**.
4. O `requirements.txt` é detectado automaticamente. A cada `git push`, o app é
   reimplantado sozinho — atualizar para a turma toda é só commitar.

## Versão desktop / executável (.exe)

Rodar a janela:

```bash
python desktop/desktop.py
```

Gerar o executável (no Windows, com o ambiente da aplicação ativo):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed desktop/desktop.py
```

O executável aparece em `dist/`. **Ressalvas:** o arquivo fica grande
(~100–300 MB por incluir numpy/matplotlib), é específico por sistema operacional
(o `.exe` é só para Windows), pode disparar alerta de antivírus/SmartScreen (a
assinatura de código resolve, mas tem custo) e, a cada mudança, é preciso
recompilar e redistribuir o arquivo. Por isso a **web é a via recomendada** para
uso em sala; o `.exe` atende cenários offline.

## Como expandir

Para adicionar um novo tópico (curvas horizontais, superelevação, etc.):

1. Crie um módulo de cálculo/plotagem em `geom_vert/` (núcleo puro).
2. Crie uma nova página `pages/2_Nome_Do_Topico.py` que importe e use esse núcleo.

O menu lateral do Streamlit passa a listar a nova página automaticamente.
```
