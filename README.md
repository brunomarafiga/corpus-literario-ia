# Projeto de Iniciação Científica - OBIA

**Observatório Brasileiro de Inteligência Artificial (OBIA)**  
**Pesquisador PIBIC:** Bruno Marafiga  
**Área:** Pipelines de Dados para IA, Web Scraping e Benchmarking de Modelos.

## 📌 Sobre o Projeto

Este repositório contém os scripts e ferramentas desenvolvidos durante a Iniciação Científica (PIBIC) no OBIA/UFPR. O foco principal é o desenvolvimento de pipelines automatizados para **coleta, tratamento e estruturação de dados** voltados para o treinamento e benchmarking de modelos de Inteligência Artificial, especificamente na geração de **embeddings**.

O projeto atual foca na criação de um **Corpus Textual Classificado** (baseado nos 4 elementos: Água, Terra, Ar, Fogo) extraído de obras literárias clássicas em domínio público.

## 🚀 Funcionalidades

- **Web Scraping Automatizado**: Coleta de textos brutos diretamente de fontes como Project Gutenberg.
- **Processamento de Linguagem Natural (NLP) Básico**:
  - Limpeza de cabeçalhos/rodapés de licenças.
  - Segmentação em parágrafos e frases.
  - Classificação temática baseada em palavras-chave.
- **Geração de Datasets Balanceados**: Criação de arquivos estruturados (`.ods` ou `.csv`) prontos para treinamento de modelos.
- **Validação de Dados**: Scripts para verificar a integridade e distribuição do corpus gerado.

## 📂 Estrutura do Projeto

- `corpus_generator.py`: Script principal. Lê as fontes, baixa os textos, processa, classifica e gera o dataset balanceado.
- `verify_corpus.py`: Script de utilidade para ler o último dataset gerado e exibir estatísticas (distribuição de classes, contagem de registros, nulos, etc.).
- `sources.json`: Arquivo de configuração contendo a lista de obras literárias (Título, Autor, URL) para extração.
- `data/`: Diretório onde os textos brutos baixados são armazenados (cache).
- `output/`: Diretório onde os datasets finais processados são salvos.

## 🛠️ Instalação e Configuração

Certifique-se de ter o **Python 3.8+** instalado.

1. Clone o repositório:
   ```bash
   git clone https://github.com/brunomarafiga/extracao_poemas.git
   cd extracao_poemas
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install pandas requests odfpy openpyxl
   ```
   *Nota: `odfpy` é necessário para suporte a arquivos .ods (OpenDocument Spreadsheet).*

## 💻 Como Usar

### 1. Gerar o Dataset
Execute o script gerador. Ele fará o download das obras listadas em `sources.json` (se ainda não estiverem na pasta `data/`) e criará um novo arquivo na pasta `output/`.

```bash
python corpus_generator.py
```

### 2. Verificar o Dataset
Para analisar a distribuição dos dados gerados e garantir que não há erros:

```bash
python verify_corpus.py
```

### 3. Adicionar Novas Fontes
Edite o arquivo `sources.json` adicionando novos objetos JSON com a estrutura:
```json
{
  "author": "Nome do Autor",
  "title": "Título da Obra",
  "url": "URL_DO_ARQUIVO_TXT"
}
```

## 📈 Próximos Passos

- [ ] **Treinamento de Embeddings**: Utilizar o dataset gerado para treinar modelos (Word2Vec, Doc2Vec ou Fine-tuning de BERT).
- [ ] **Benchmarking**: Comparar a qualidade dos embeddings gerados com modelos pré-treinados em tarefas de similaridade semântica e classificação.
- [ ] **Integração com LLMs**: Avaliar o desempenho em tarefas de RAG (Retrieval-Augmented Generation).

---
*Projeto desenvolvido como parte das atividades de pesquisa do OBIA - UFPR.*

## Contexto do projeto

Pipeline de pesquisa desenvolvido no OBIA/UFPR para coleta, limpeza, segmentação e classificação temática de textos literários. O projeto organiza fontes públicas em datasets estruturados para experimentos de NLP e embeddings.

**Temas:** Python, web scraping, NLP, datasets e inteligência artificial.

[Ver repositório](https://github.com/brunomarafiga/extracao_poemas)
