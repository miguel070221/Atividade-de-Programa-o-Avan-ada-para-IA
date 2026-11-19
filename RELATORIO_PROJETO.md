# Projeto de Programação — Painel de Monitoramento de Nascimentos

## Capa

**Sistema:** Painel de Monitoramento de Nascimentos no Grande ABC  
**Disciplina:** Programação Avançada para a IA  
**Integrantes:** Thiago Silva, Thiago Alves, Beatriz Mayumi, Samuel Castro e Miguel Buglio  
**Divisão dos gráficos:** 1–2 — Thiago Silva; 3–4 — Thiago Alves; 5–6 — Beatriz Mayumi; 7–8 — Samuel Castro; 9–11 — Miguel Buglio  
**Base:** SINASC 2026 — Ministério da Saúde

## 1. Introdução

Este projeto apresenta um painel de monitoramento de nascimentos nos sete municípios do Grande ABC paulista: Diadema, Mauá, Ribeirão Pires, Rio Grande da Serra, Santo André, São Bernardo do Campo e São Caetano do Sul.

O painel foi desenvolvido em Python com Streamlit, Pandas e Plotly. O arquivo nacional do SINASC é lido com apenas as colunas necessárias para reduzir o consumo de memória. Em seguida, os registros são filtrados pelo código de residência do município. Como o SINASC usa os seis primeiros dígitos do código IBGE, os códigos são associados à base `IBGE_municipios.csv` usando essa parte comum.

As categorias codificadas foram traduzidas com base no `codebook-SINASC.pdf`. Datas são convertidas para análise mensal, campos numéricos são convertidos para números e valores ignorados ou não informados são mantidos por padrão. O usuário pode ocultar essas categorias pelo filtro lateral.

## 2. Funcionalidades principais

O painel contém filtros por município, período de nascimento e categorias ignoradas. Após a filtragem, todos os gráficos são atualizados automaticamente. Foram implementadas as 11 análises sugeridas no enunciado:

1. evolução mensal dos nascimentos;
2. distribuição por tipo de parto;
3. duração da gestação;
4. distribuição do peso ao nascer;
5. peso ao nascer por sexo;
6. consultas pré-natais;
7. proporção de partos por faixa etária materna;
8. distribuição por raça/cor;
9. distribuição por município de residência;
10. tipo de gravidez;
11. escolaridade materna e tipo de parto.

Cada gráfico está identificado no painel com o integrante correspondente: Thiago Silva nos gráficos 1 e 2;
Thiago Alves nos gráficos 3 e 4; Beatriz Mayumi nos gráficos 5 e 6; Samuel Castro nos gráficos 7 e 8;
e Miguel Buglio nos gráficos 9, 10 e 11.

### 2.1. Operação importante: filtragem da região do ABC

O filtro transforma `CODMUNRES` em texto, completa o código com zeros quando necessário e seleciona somente os códigos dos sete municípios:

```python
ABC_CODIGOS = {
    "351380": "Diadema",
    "352940": "Mauá",
    "354330": "Ribeirão Pires",
    "354410": "Rio Grande da Serra",
    "354780": "Santo André",
    "354870": "São Bernardo do Campo",
    "354880": "São Caetano do Sul",
}

dados["CODMUNRES"] = dados["CODMUNRES"].str.zfill(6)
dados = dados[dados["CODMUNRES"].isin(ABC_CODIGOS)].copy()
dados["Município"] = dados["CODMUNRES"].map(ABC_CODIGOS)
```

Essa operação é essencial porque a fonte contém registros do Brasil inteiro. Na base fornecida, o recorte do Grande ABC possui 15.865 registros.

### 2.2. Operação importante: preparação dos campos

As datas e os campos quantitativos são convertidos para permitir agrupamentos, médias e gráficos estatísticos:

```python
dados["Data de nascimento"] = pd.to_datetime(
    dados["DTNASC"], format="%d%m%Y", errors="coerce"
)
for coluna in ["IDADEMAE", "PESO", "SEMAGESTAC", "CONSPRENAT"]:
    dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")
```

Para melhorar a leitura do painel, os códigos de parto, sexo, raça/cor, gravidez, gestação e escolaridade são substituídos pelos rótulos descritos no codebook.

### 2.3. Operação importante: geração de proporções por faixa etária

Para analisar a composição dos partos, as idades são agrupadas em faixas e a tabela cruzada é normalizada por linha:

```python
idade_parto["Faixa etária"] = pd.cut(
    idade_parto["IDADEMAE"],
    bins=[0, 19, 24, 29, 34, 39, 200],
    labels=["Até 19", "20–24", "25–29", "30–34", "35–39", "40+"],
    include_lowest=True,
)
proporcao = pd.crosstab(
    idade_parto["Faixa etária"],
    idade_parto["Tipo de parto"],
    normalize="index",
)
```

A normalização permite comparar as faixas mesmo quando elas possuem quantidades diferentes de registros.

## 3. Resultados e discussão

O recorte fornecido contém registros de janeiro a agosto de 2026. Os municípios com maior quantidade de registros são São Bernardo do Campo e Santo André, seguidos por Mauá e Diadema. O painel permite confirmar e detalhar essas diferenças por período, tipo de parto, gestação, consultas pré-natais, raça/cor, gravidez e escolaridade.

Os gráficos de peso utilizam a faixa de 300 g a 7.000 g para evitar que códigos fora da faixa plausível distorçam o histograma e o boxplot. A idade materna é comparada entre 10 e 60 anos nas análises por faixa etária. Esses critérios não alteram a contagem geral do painel; eles se aplicam apenas às visualizações quantitativas correspondentes.

## 4. Conclusão

O projeto resultou em um painel funcional, local e interativo para exploração dos nascimentos no Grande ABC. A atividade permitiu praticar leitura de dados delimitados, filtragem de uma base nacional, tratamento de variáveis codificadas, criação de indicadores derivados e construção de gráficos com Plotly.

Como melhorias futuras, o grupo poderia incluir uma atualização automática da fonte do DATASUS, um mapa coroplético dos municípios, exportação de relatórios filtrados e comparação entre diferentes anos do SINASC. Também é possível acrescentar controles para selecionar a variável de gestação categórica ou numérica.

## 5. Como executar

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

O relatório deve ser complementado pela equipe com os nomes completos dos integrantes, capturas de tela do painel e eventuais observações da apresentação oral.
