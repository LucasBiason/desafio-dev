# Glossário

| Termo | Definição |
|-------|-----------|
| CNAB | Centro Nacional de Automação Bancária. Padrão brasileiro de arquivo texto para transações financeiras |
| Transação | Movimentação financeira registrada no arquivo CNAB |
| Loja | Estabelecimento comercial que realiza transações |
| Dono da Loja | Representante/proprietário do estabelecimento |
| Natureza | Classificação da transação: Entrada (receita) ou Saída (despesa) |
| Sinal | Indicador positivo (+) ou negativo (-) para cálculo do saldo |
| Saldo | Resultado da soma de entradas menos saídas de uma loja |
| Upload | Processo de envio do arquivo CNAB para o sistema |
| Parsing | Processo de leitura e interpretação dos campos de largura fixa |
| Normalização | Conversão dos dados brutos para formato adequado (ex: valor / 100) |
| CPF | Cadastro de Pessoa Física, documento de identificação brasileiro |
| Largura Fixa | Formato de arquivo onde cada campo ocupa posições predefinidas |
| Microsserviço | Serviço com responsabilidade única, banco de dados próprio e implantação independente |
| Fernet | Esquema de criptografia simétrica usado na comunicação entre upload-service e cnab-service. Gera tokens com expiração automática (TTL) impossíveis de forjar sem a chave compartilhada |
| content_hash | Hash SHA-256 calculado a partir dos campos da transação para identificar duplicatas. Transações com o mesmo hash são ignoradas na inserção |
| Deduplicação | Mecanismo que impede a inserção de transações duplicadas. Baseia-se no campo content_hash da tabela cnab_transaction |
| Worker | Processo em background (upload-worker) que faz polling no banco a cada 10 segundos buscando uploads pendentes e os envia em lotes de 1000 transações ao cnab-service |
| Dashboard | Painel analítico de conciliação bancária servido pelo cnab-dashboard. Organizado em três camadas: Panorama (KPIs), Desempenho (gráficos) e Operação (detalhamento) |
| Seed | Dados iniciais inseridos via migration. Os 9 tipos de transação CNAB são carregados por seed na tabela cnab_transaction_type |
