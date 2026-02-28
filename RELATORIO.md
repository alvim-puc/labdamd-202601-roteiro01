# RELATÓRIO TÉCNICO — Roteiro 2

## Questão 1 — Backlog e Recusa de Conexões

Durante os testes, foi observado que o `servergargalo.py` opera em modo monotarefa (bloqueante), executando `accept()`, atendendo apenas uma conexão por vez e permanecendo aproximadamente 5 segundos em `time.sleep(5)` antes de voltar a aceitar novas conexões. Dessa forma, enquanto uma conexão está em atendimento, as demais tentativas ficam dependendo diretamente da fila de conexões pendentes gerenciada pelo sistema operacional.

Como o servidor foi configurado com `listen(1)`, foi percebido que a fila solicitada ao SO é propositalmente pequena e, sob rajada de 10 clientes simultâneos (`clientenervoso.py`), tende a saturar rapidamente. A partir desse ponto, o comportamento observado varia conforme a implementação do sistema operacional e o tempo limite definido no cliente. Em parte das execuções ocorre `ConnectionRefusedError` (recusa imediata), enquanto em outras ocorre `socket.timeout`, pois a conexão não é concluída dentro do prazo estabelecido.

Por outro lado, no `server.py`, foi verificado que cada conexão aceita é delegada para uma thread própria. Com isso, o laço principal retorna mais rapidamente ao `accept()` e continua consumindo a fila, reduzindo significativamente a chance de saturação do backlog no mesmo cenário de carga. Assim, em comparação com o servidor monotarefa, o `clientenervoso.py` tende a obter conexão com maior sucesso no servidor multithread.

## Questão 2 — Custo de Recursos: Threads vs. Event Loop

### Observação experimental

No teste com 10 clientes simultâneos, foi observado que o `server.py` eleva o valor exibido em `threading.active_count() - 1` até próximo do tamanho da rajada, atingindo pico em torno de 10 threads de trabalho ativas, além da thread principal.

### Análise técnica

Com base nessa observação, foi percebido que a abordagem multithread (`server.py`) melhora de forma importante o tempo de resposta sob concorrência quando comparada ao modo monotarefa, porém esse ganho vem acompanhado de maior consumo de recursos do sistema operacional. Isso ocorre porque cada cliente passa a ocupar uma thread própria durante o período de espera e processamento, o que implica custo de criação e gerenciamento de threads, além do consumo de memória de stack por conexão ativa.

Também foi verificado que, à medida que o número de conexões simultâneas aumenta, cresce a necessidade de troca de contexto (*context switch*) entre threads, elevando o overhead de CPU. Em cargas maiores, esse custo tende a se tornar fator limitante de escalabilidade.

Na abordagem assíncrona (`server_async.py`), por sua vez, foi observado que o servidor mantém uma única thread com Event Loop e múltiplas corrotinas cooperativas. Para tanto, ao utilizar `await asyncio.sleep(5)`, a corrotina é suspensa sem bloquear a thread principal, permitindo que outras conexões avancem no mesmo período. Como consequência, há redução expressiva do overhead estrutural por conexão, especialmente em cenários predominantemente I/O-bound.

Dessa forma, para a mesma carga de 10 clientes, conclui-se que o modelo multithread já representa melhora relevante frente ao monotarefa, mas o modelo assíncrono apresenta melhor eficiência de uso de CPU e memória, com maior potencial de escalabilidade para aumento de concorrência.

## _Disclaimer_ acerca de `clientenervoso.py`

Durante os testes, foi percebido que o script que executar 10 requisições simultaneas gera timeout até em situações que não deveriam. Para tanto, com o objetivo de contornar esse _bug_, o timeout de 2s para conexão foi mantido. Entretanto, um novo timeout foi definido para contemplar o tempo de processamento `sleep(5)` dos servidores, que é de 5s.