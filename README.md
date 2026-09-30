# Simulação de rodízio docente

Simulador em Python da distribuição de disciplinas por **fila persistente**, com pontuação documental para ingresso e precedência da correspondência de área. Os docentes, suas trajetórias e as ofertas são inteiramente fictícios. O código não consulta cadastros institucionais nem serviços externos.

O objetivo é permitir a reprodução e a inspeção dos resultados exploratórios da proposta de atribuição docente. O simulador não é um sistema de atribuição em produção e não substitui avaliação institucional com dados reais.

## Executar

Requer Python 3.11 ou posterior. Utiliza somente a biblioteca padrão, sem instalações adicionais.

```bash
git clone https://github.com/acandreani/simulacao-rodizio-docente.git
cd simulacao-rodizio-docente
python3 -m unittest -v
python3 simular.py
```

Para preservar os resultados de referência e gerar outra cópia:

```bash
python3 simular.py --saida resultados_novos
```

Não execute os testes com a opção `-O`, que desativa as verificações internas feitas com `assert`.

## Regra representada

1. A pontuação organiza a fila inicial e cada lote de novos inscritos. Em empate, precede quem nunca ministrou; depois, quem está há mais tempo sem ministrar; persistindo o empate, há sorteio reproduzível.
2. Novos inscritos entram depois dos participantes existentes, mesmo quando possuem pontuação maior.
3. Quem é chamado e não pode assumir vai ao fim. Quem assume também vai ao fim. Cada participante é chamado no máximo uma vez por oferta.
4. A fila principal, de correspondência de área comprovada, tem precedência. A subsidiária só é consultada quando nenhum participante da principal está disponível.
5. A experiência aumenta após a regência, até o teto de pontuação, sem reordenar a fila existente.

O campo `area` representa uma correspondência documental já verificada entre a área da disciplina declarada no PPC e a classificação oficial pertinente ao título, referenciada pela CAPES. O código não realiza essa análise documental.

A função `base` calcula aderência (60 ou 0), nível do título aderente (8, 12, 16 ou 20), experiência didática (até 12) e profissional (até 8). A experiência didática atinge o teto em 360 horas e a profissional em 720 dias. A função também aceita a tabela alternativa de 8 e 12 pontos para essas experiências, mas os resultados publicados usam a tabela padrão. Sem correspondência de área, o título não pontua; apenas as experiências são computadas.

## Experimentos e reprodução

São **121 execuções**: 21 cenários predefinidos e 100 equipes com disponibilidade sorteada, no horizonte de vinte anos, a partir de janeiro de 2026. Essas datas são parâmetros fictícios.

Os cenários incluem equipes estáveis, ingressos e saídas, afastamentos, crescimento contínuo e mudança de periodicidade. Há uma vaga por oferta, inicialmente semestral. No cenário `periodicidade_muda`, as ofertas passam a anuais em 2032. Cada regência concluída acrescenta 60 horas de experiência didática.

As cem equipes têm 2, 3, 5, 9 ou 12 integrantes, com vinte repetições por tamanho. Os perfis iniciais são sorteados entre 68, 80, 86 e 100 pontos. Fora de afastamentos, cada docente tem 80% de chance de estar disponível em cada oferta. Há 35% de chance por docente de incluir um afastamento entre janeiro de 2032 e janeiro de 2034. Usa-se a semente `20261001 + n * 1000 + rep`, onde `rep` varia de 0 a 19. Os cenários predefinidos usam a semente 1.

O sorteio de desempate é uma aproximação computacional. Em aplicação administrativa, seria necessário um procedimento público e registrado.

| Cenário | Resultado em quarenta ofertas |
| --- | --- |
| Cinco docentes estáveis | Oito atribuições por pessoa |
| Doze docentes estáveis | Três ou quatro atribuições por pessoa |
| Dois iniciais, mais um ingresso por semestre durante 39 semestres | B recebe quatro atribuições; vinte dos 41 participantes terminam sem atribuição |
| Dois iniciais, mais dois ingressos por semestre durante 39 semestres | B recebe três atribuições; 53 dos oitenta participantes terminam sem atribuição |

Nos cenários de crescimento, A começa com 100 pontos e B com 68; os ingressantes têm 68 pontos. B recebe sua primeira atribuição na segunda oferta. O crescimento é um teste extremo, não uma previsão de contratação. Ausência de atribuição ao fim do horizonte não demonstra exclusão permanente.

Nas cem equipes de disponibilidade variável, todos os participantes receberam ao menos uma atribuição; a maior sequência observada foi de seis atribuições à mesma pessoa. Esses resultados não garantem alternância em toda oferta nem atendimento em prazo fixo.

## Arquivos e métricas

| Arquivo | Conteúdo |
| --- | --- |
| `modelo.py` | Perfis, pontuação e operações de calendário |
| `cenarios.py` | Construção dos 21 cenários sintéticos |
| `fila.py` | Motor de distribuição e registros de indisponibilidade |
| `simular.py` | Execução e exportação dos resultados |
| `test_fila.py` | Casos analíticos, precedência, conservação e reprodução |
| `resultados/resultados.json` | Contagens, sequências e eventos dos 21 cenários |
| `resultados/memoria_fila.csv` | Pontuação e seleção por participante disponível e oferta |
| `resultados/sensibilidade.csv` | Indicadores das cem equipes sorteadas |
| `resultados/execucao.json` | Parâmetros gerais e sementes |

`maior_sequencia` conta ofertas consecutivas atribuídas à mesma pessoa. `maior_espera` conta ofertas em que a pessoa estava disponível e não foi selecionada, acumuladas desde a última atribuição; não mede tempo corrido nem posição na fila. `sem_atribuicao` considera apenas quem esteve disponível em pelo menos uma oferta. Uma pessoa nunca disponível pode aparecer com zero em `contagens` sem entrar nesse indicador.

Na memória CSV, `posicao` é a posição na lista interna depois dos deslocamentos dos indisponíveis daquela oferta e antes do deslocamento de quem assume. A precedência da principal é aplicada separadamente: esse número não deve ser interpretado como uma classificação única entre as duas filas. A memória registra candidatos disponíveis, enquanto os eventos registram os chamados indisponíveis.

Os nomes A, B, C, P0 e E01_0 são identificadores sintéticos, sem associação a pessoas reais. Os cenários principais têm correspondência de área; a relação entre principal e subsidiária é verificada nos testes dirigidos.

## Limites

As ofertas são sequenciais e têm um único responsável. A aceitação e o início da regência são tratados como um único evento. Não estão implementados cancelamento, saída seguida de reinscrição, mudança entre filas, alocação global de carga e horários, regência compartilhada ou múltiplas ofertas simultâneas. A atualização cadastral administrativa e os procedimentos de publicação e recurso não são simulados.

Os testes não medem aprendizagem, continuidade pedagógica, custos de preparação ou adequação jurídica. A concentração depende também da disponibilidade: um único docente disponível pode receber ofertas consecutivas.

## Dados e publicação

O repositório contém somente código, documentação técnica e resultados sintéticos. Não inclui a minuta, documentos particulares, manifestações individuais, dados de docentes reais, vídeos, credenciais ou arquivos de configuração da hospedagem.

Esta edição autônoma preserva o cálculo e a ordem dos sorteios da simulação usada na proposta. Antes da publicação, os resultados dos 21 cenários, a memória e as cem equipes foram conferidos contra os arquivos de referência. Três nomes internos de cenários foram substituídos por `historico_recente_todos_2`, `historico_recente_todos_5` e `historico_recente_todos_12`, para descrever suas condições iniciais.
