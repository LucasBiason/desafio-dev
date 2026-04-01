# Problem Statement

## Problema

Empresas que operam com múltiplas lojas recebem arquivos CNAB contendo transações financeiras em formato texto de largura fixa. Esses dados precisam ser importados, normalizados e visualizados de forma organizada para controle financeiro.

## Objetivo

Construir uma aplicação web que:

1. Aceite upload de arquivos CNAB via formulário
2. Parse e normalize os dados de largura fixa
3. Armazene em banco de dados relacional
4. Exiba transações agrupadas por loja com saldo totalizado

## Critérios de Aceite (Obrigatórios)

- [ ] Formulário de upload de arquivo CNAB funcional
- [ ] Parsing correto dos campos de largura fixa (tipo, data, valor, CPF, cartão, hora, dono, loja)
- [ ] Normalização do valor (dividir por 100)
- [ ] Armazenamento em PostgreSQL
- [ ] Listagem de transações agrupadas por loja
- [ ] Totalizador de saldo por loja (entradas - saídas)
- [ ] Testes automatizados com boa cobertura
- [ ] Docker Compose funcional
- [ ] README com instruções de setup
- [ ] Documentação de consumo da API
- [ ] Commits atômicos e bem descritos

## Critérios Bônus

- [ ] Autenticação/autorização (JWT)
- [ ] CSS customizado (sem framework popular)
- [ ] Documentação completa da API (Swagger/Redoc)

## Formato CNAB

Arquivo texto com linhas de 81 caracteres, campos de largura fixa:

| Campo | Início | Fim | Tamanho | Descrição |
|-------|--------|-----|---------|-----------|
| Tipo | 1 | 1 | 1 | Tipo da transação (1-9) |
| Data | 2 | 9 | 8 | YYYYMMDD |
| Valor | 10 | 19 | 10 | Valor da movimentação. *Obs.* O valor encontrado no arquivo precisa ser divido por cem(valor / 100.00) para normalizá-lo. |
| CPF | 20 | 30 | 11 | CPF do beneficiário |
| Cartão | 31 | 42 | 12 | Cartão mascarado |
| Hora | 43 | 48 | 6 | Hora da ocorrência atendendo ao fuso: HHMMSS (UTC-3) |
| Dono Loja | 49 | 62 | 14 | Nome do representante da loja |
| Nome Loja | 63 | 81 | 19 | Nome da loja |

## Tipos de Transação

| Tipo | Descrição | Natureza | Sinal |
|------|-----------|----------|-------|
| 1 | Débito | Entrada | + |
| 2 | Boleto | Saída | - |
| 3 | Financiamento | Saída | - |
| 4 | Crédito | Entrada | + |
| 5 | Recebimento Empréstimo | Entrada | + |
| 6 | Vendas | Entrada | + |
| 7 | Recebimento TED | Entrada | + |
| 8 | Recebimento DOC | Entrada | + |
| 9 | Aluguel | Saída | - |
