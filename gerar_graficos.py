"""Gera os gráficos e a tabela do README a partir dos resultados publicados."""
import csv
import json
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs' / 'graficos'
START = '<!-- inicio: resultados visuais gerados -->'
END = '<!-- fim: resultados visuais gerados -->'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = {r['cenario']: r for r in json.loads((ROOT / 'resultados/resultados.json').read_text())}
    with (ROOT / 'resultados/sensibilidade.csv').open(encoding='utf-8-sig', newline='') as stream:
        sensitivity = list(csv.DictReader(stream))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.titleweight': 'bold', 'figure.facecolor': 'white',
                         'axes.facecolor': 'white', 'savefig.facecolor': 'white'})

    def save(fig, filename):
        fig.savefig(OUT / filename, dpi=160, bbox_inches='tight', metadata={'Software': 'Matplotlib'})
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout='constrained', sharey=True)
    for ax, n, key in zip(axes, [5, 12], ['cinco_estaveis', 'doze_estaveis']):
        counts = cases[key]['contagens']
        bars = ax.bar(list(counts), list(counts.values()), color='#245b85', width=.68)
        ax.bar_label(bars, padding=4)
        ax.set_title(f'{n} docentes')
        ax.set_xlabel('Docente fictício')
        ax.set_ylim(0, 10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_axisbelow(True)
        ax.grid(axis='y', alpha=.18)
    axes[0].set_ylabel('Atribuições por docente')
    fig.suptitle('Equipes estáveis: distribuição de 40 ofertas', fontsize=15, fontweight='bold')
    save(fig, 'equipes_estaveis.png')

    fig, ax = plt.subplots(figsize=(11, 4.5), layout='constrained')
    labels = ['1 ingresso por semestre\n41 participantes ao final',
              '2 ingressos por semestre\n80 participantes ao final']
    for i, rate in enumerate([1, 2]):
        result = cases[f'crescimento_{rate}_por_semestre_durante_39']
        served = sum(v > 0 for v in result['contagens'].values())
        unserved = sum(v == 0 for v in result['contagens'].values())
        ax.barh(i, served, color='#245b85', label='Recebeu ao menos uma atribuição' if i == 0 else None)
        ax.barh(i, unserved, left=served, color='#d5dce3', label='Sem atribuição ao final' if i == 0 else None)
        ax.text(served / 2, i, str(served), ha='center', va='center', color='white', fontweight='bold')
        ax.text(served + unserved / 2, i, str(unserved), ha='center', va='center', color='#172b3a', fontweight='bold')
    ax.set_yticks([0, 1], labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 85)
    ax.set_xlabel('Número de participantes distintos (não de atribuições)')
    ax.set_title('Crescimento contínuo: atendimento ao fim de 40 ofertas', pad=18)
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.24), ncol=2, frameon=False)
    save(fig, 'crescimento_continuo.png')

    sizes = [2, 3, 5, 9, 12]
    groups = [[int(r['maior_sequencia']) for r in sensitivity if int(r['n']) == n] for n in sizes]
    assert all(len(g) == 20 for g in groups)
    fig, ax = plt.subplots(figsize=(10, 4.8), layout='constrained')
    # Cada ponto representa uma execução; deslocamento horizontal apenas para evitar sobreposição.
    for i, values in enumerate(groups):
        for value in sorted(set(values)):
            total = values.count(value)
            xs = [i + (j - (total - 1) / 2) * .035 for j in range(total)]
            ax.scatter(xs, [value] * total, s=32, color='#245b85', alpha=.85)
        ax.plot([i - .3, i + .3], [median(values)] * 2, color='#b65b22', linewidth=3,
                label='Mediana das 20 execuções' if i == 0 else None)
    ax.set_xticks(range(len(sizes)), [str(n) for n in sizes])
    ax.set_xlabel('Número de docentes na equipe')
    ax.set_ylabel('Maior sequência de atribuições\nà mesma pessoa em cada execução')
    ax.set_title('Disponibilidade variável: repetições observadas', pad=18)
    ax.set_ylim(.5, max(max(g) for g in groups) + .6)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc='upper right')
    save(fig, 'disponibilidade_variavel.png')

    table = ['| Docentes por equipe | Execuções | Ofertas preenchidas (mín.–máx., de 40) | Maior sequência observada | Execuções em que todos receberam atribuição |',
             '| ---: | ---: | ---: | ---: | ---: |']
    for n in sizes:
        group = [r for r in sensitivity if int(r['n']) == n]
        filled = [int(r['atribuicoes']) for r in group]
        sequence = max(int(r['maior_sequencia']) for r in group)
        all_served = sum(int(r['sem_atribuicao']) == 0 for r in group)
        table.append(f'| {n} | {len(group)} | {min(filled)}–{max(filled)} | {sequence} | {all_served} |')

    section = '''### Resultados visuais

Os gráficos abaixo usam exclusivamente os arquivos de resultados deste repositório. Todos os participantes são fictícios.

**Equipes estáveis.** Sem entradas, saídas ou indisponibilidade, a diferença de atribuições entre docentes fica em, no máximo, uma oferta nos dois cenários apresentados. A pontuação inicial não impede a alternância depois da formação da fila.

![Dois gráficos de barras: cinco docentes recebem oito atribuições cada; doze docentes recebem três ou quatro atribuições cada.](docs/graficos/equipes_estaveis.png)

**Crescimento contínuo.** As barras contam pessoas distintas, e não ofertas. A equipe começa com dois docentes e recebe novos inscritos por 39 semestres. O número de participantes cresce mais depressa que o de vagas. Quem ainda não recebeu uma atribuição ao fim de vinte anos não está necessariamente excluído para sempre; o horizonte observado terminou.

![Atendimento em crescimento contínuo: entre 41 participantes, 21 recebem atribuição e vinte não; entre oitenta, 27 recebem e 53 não.](docs/graficos/crescimento_continuo.png)

**Disponibilidade variável.** Cada ponto representa uma das cem execuções, com vinte equipes de cada tamanho. A linha laranja marca a mediana. A maior sequência é calculada separadamente em cada execução: ela não representa a quantidade total de atribuições de um docente. A indisponibilidade dos demais pode permitir repetições.

![Distribuição da maior sequência de atribuições à mesma pessoa, por tamanho de equipe. Valores exatos e número de execuções estão na tabela abaixo.](docs/graficos/disponibilidade_variavel.png)

''' + '\n'.join(table) + '''

Cada execução tem quarenta ofertas. Uma oferta fica sem preenchimento quando ninguém pode assumir. Fora dos afastamentos, a probabilidade de disponibilidade é de 80% por docente e oferta. Todos os participantes dessas cem equipes estiveram disponíveis em alguma oferta; por isso, o indicador de ausência de atribuição permite a contagem da última coluna neste conjunto. Esses resultados são exploratórios e não garantem atendimento em outras condições.

Fontes: [cenários e sequências](resultados/resultados.json) e [cem equipes de disponibilidade variável](resultados/sensibilidade.csv).
'''
    readme = ROOT / 'README.md'
    text = readme.read_text()
    block = START + '\n' + section + '\n' + END
    if START in text:
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        text = before + block + after
    else:
        text = text.replace('## Arquivos e métricas', block + '\n\n## Arquivos e métricas')
    readme.write_text(text)
    print('Três gráficos e tabela do README atualizados.')


if __name__ == '__main__':
    main()
