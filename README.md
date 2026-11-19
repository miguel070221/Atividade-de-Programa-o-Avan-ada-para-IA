# Painel de Monitoramento de Nascimentos

Aplicação em Python/Streamlit para analisar os registros do SINASC 2026 nos sete municípios do Grande ABC:
Diadema, Mauá, Ribeirão Pires, Rio Grande da Serra, Santo André, São Bernardo do Campo e São Caetano do Sul.

## Como executar

Na pasta do projeto, crie um ambiente virtual (opcional, mas recomendado) e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\\Scripts\\activate       # Windows
python -m pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá o painel localmente. No repositório, a aplicação usa a versão compactada
`Conteudo/SINASC_2026_ABC.csv.gz`, que contém somente os registros do Grande ABC. Localmente,
ela também aceita `Conteudo/SINASC_2026.csv` como alternativa e lê `Conteudo/IBGE_municipios.csv`.

## O que foi implementado

O painel tem filtros por município, período e categorias ignoradas, além dos 11 gráficos sugeridos no enunciado:

1. Evolução mensal dos nascimentos;
2. Tipo de parto;
3. Duração da gestação;
4. Distribuição do peso ao nascer;
5. Peso por sexo;
6. Consultas pré-natais;
7. Tipo de parto por faixa etária da mãe;
8. Raça/cor;
9. Município de residência;
10. Tipo de gravidez;
11. Escolaridade materna e tipo de parto.

Os gráficos 9, 10 e 11 estão identificados no painel com o nome **Miguel**.

## Decisões de tratamento

- O SINASC usa códigos de seis dígitos para `CODMUNRES`; eles são associados aos códigos IBGE de sete dígitos usando os seis primeiros dígitos.
- As categorias das variáveis foram traduzidas com base no `Conteudo/codebook-SINASC.pdf`.
- Para o peso e a idade materna, os gráficos quantitativos removem somente valores fora de faixas plausíveis (300–7.000 g e 10–60 anos).
- Valores ignorados e não informados aparecem por padrão e podem ser ocultados pelo filtro lateral.
