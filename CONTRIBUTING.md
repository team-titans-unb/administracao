# Guia de Contribuição para Documentação

Este repositório segue um padrão colaborativo para organização da documentação. Siga as orientações abaixo para mantermos um fluxo de trabalho claro e eficiente.

## Branches

Use nomes curtos, descritivos e separados por hífens:

| Tipo          | Padrão de nome              | Exemplo                      |
|---------------|-----------------------------|------------------------------|
| Funcionalidade| feature/nome-curto          | feature/pagina-software      |
| Correção      | fix/descricao               | fix/erro-ortografia          |
| Documento     | doc/tipo-de-arquivo         | doc/esquematico-bio-v2       |
| Refatoração   | refactor/parte              | refactor/paginas-bio-v2      |

## Commits

Formato: `<tipo>: <descrição breve>`

### Tipos comuns:

- `feat`: nova funcionalidade ou artefato
- `fix`: correção de erro
- `doc`: atualização de documentação
- `refactor`: reorganização sem alterar conteúdo
- `style`: ajustes de formatação ou layout
- `chore`: tarefas gerais

### Exemplos:

- `doc: adicionar esquemático do Bio-V2`
- `feat: adicionar visualizador do modelo 3D`
- `fix: corrigir tabela de pinagem`
- `refactor: reorganizar seções da página de eletrônica`

## Issues

Use títulos claros e rótulos como: `documentação`, `revisão`, `bug`, `mecânica`, `eletrônica`, `controle`, `software`, `dúvida`.

### Exemplo:

**Título:** `[documentação] Adicionar esquemático da placa principal do Bio-V2`

**Descrição:**

```markdown
## Tarefa
Adicionar o esquemático da placa principal na página de eletrônica do Bio-V2.

## Checklist
- [ ] Criar branch doc/esquematico-bio-v2
- [ ] Exportar o esquemático em PDF e PNG para docs/pages/bioV2/dados/
- [ ] Preencher as tabelas de alimentação e pinagem
```

## Pull Requests (PRs)

**Título:** `[documentação] Adicionar esquemático da placa principal do Bio-V2`

**Corpo do PR:**
```markdown
## O que foi feito
- Adicionado o esquemático da placa principal
- Preenchidas as tabelas de alimentação e pinagem

## Issue relacionada
Closes #12

## Checklist
- [x] Texto revisado
- [x] Imagens adicionadas
```

## Template de PR

O template usado nos PRs está em `.github/pull_request_template.md`.

## Padrão das páginas

Cada área da administração tem uma pasta em `docs/pages/` (ex.: `docs/pages/inventario/`) com:

| Arquivo | Conteúdo |
| :--- | :--- |
| `index.md` | Visão geral da área e suas tabelas principais |
| outras páginas `.md` | Subtemas da área, quando a página principal ficar grande |
| `dados/` | Imagens, PDFs, planilhas e demais arquivos usados nas páginas |

| Área | Pasta |
| :--- | :--- |
| Membros | `docs/pages/membros/` |
| Inventário | `docs/pages/inventario/` |
| Viagens | `docs/pages/viagens/` |

Toda página termina com a tabela **Histórico de Versões**. Ao alterar uma página, adicione uma linha nova com a versão incrementada (`1.0` → `1.1`), a descrição, o autor e a data.

Ao criar uma nova área, copie a pasta de uma área existente, renomeie, adicione as páginas no `nav` do `mkdocs.yml` e inclua uma linha na tabela **Áreas** da Home (`docs/index.md`).

## Recursos de escrita

| Recurso | Como escrever |
| :--- | :--- |
| Campo a preencher (aparece em vermelho) | `<mark>[ex.: Jetson Orin Nano]</mark>` |
| Aviso | `!!! note "Título"`, `!!! tip`, `!!! warning` ou `!!! info`, com o texto na linha de baixo recuado 4 espaços |
| Fórmula no texto | `$\frac{TP}{TP + FP}$` |
| Fórmula em bloco | `$$` em uma linha, a fórmula, e `$$` na linha seguinte (com linha em branco antes e depois) |
| Diagrama | bloco de código com a linguagem `mermaid` |
| Bloco de código com nome de arquivo | ` ```yaml title="data.yaml" ` |
| Imagem centralizada | `<div align="center" markdown>` + `![Descrição](dados/imagem.png){ width="600" }` + `</div>` |
| Nota pequena sob uma tabela | `<div class="nota-tabela" markdown>` + texto + `</div>` |
| Quebra de linha dentro de tabela | `<br>` |

As tabelas são escritas em Markdown comum; o estilo da Titans (cabeçalho laranja, linhas alternadas, primeira coluna em negrito) é aplicado automaticamente por `docs/overrides/tabelas.css`.

## Para documentar

Siga os seguintes passos para visualizar a documentação localmente:

```markdown
# Instalar o MkDocs e o tema Material 
pip install -r requirements.txt

# Visualizar o site localmente
mkdocs serve
```

## Deploy

O deploy para o GitHub Pages é feito automaticamente pelo GitHub Actions (`.github/workflows/deploy.yml`) a cada push na `main`. Para fazer manualmente:

```markdown
# Realizar o deploy para o GitHub Pages
mkdocs gh-deploy
```
