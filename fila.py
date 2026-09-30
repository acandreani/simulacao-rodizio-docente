"""Fila persistente, com precedência da correspondência de área comprovada."""
from collections import Counter
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as F
import random
from modelo import START, addmonths, base

def queue_run(people,years=20,seed=1,interest=1.,period_change=False):
    people=deepcopy(people);rng=random.Random(seed)
    dates=[];now=START
    while now<addmonths(START,12*years):
        interval=12 if period_change and now.year>=2032 else 6
        dates.append((now,interval));now=addmonths(now,interval)
    # Sorteios reproduzíveis de disponibilidade e desempate, independentes por oferta.
    draws=[[(rng.random(),rng.random()) for p in people] for _ in dates]
    queue=[];entered=set();counts=Counter();participated=Counter();runs=Counter();losses=Counter()
    rows=[];sequence=[];events=[];maxrun=maxwait=0
    for k,(now,interval) in enumerate(dates):
        for p in people:
            t=p.teacher
            finished=[x for x in t.pending if x[0]<now]
            t.hours+=sum((h for _,h in finished),F(0))
            t.pending=[x for x in t.pending if x[0]>=now]
        queue=[j for j in queue if now<people[j].exit]
        new=[j for j,p in enumerate(people) if p.entry<=now<p.exit and j not in entered]
        def entrykey(j):
            t=people[j].teacher
            return base(t),t.last_end is None,-t.last_end.toordinal() if t.last_end else 0,draws[k][j][1]
        # Registro inicial/lote de ingresso ordenado por base; não reordena veteranos.
        new.sort(key=entrykey,reverse=True);queue.extend(new);entered.update(new)
        eligible=[j for j in queue if people[j].can(now) and draws[k][j][0]<interest]
        primary=[j for j in queue if people[j].teacher.area]
        secondary=[j for j in queue if not people[j].teacher.area]
        called=[];winner=None
        # Chama na ordem, uma vez por oferta. Indisponível perde a vez e vai ao fim.
        # As faixas de aderência são distintas; fila subsidiária só após esgotar a principal.
        for band in [primary,secondary]:
            for j in band:
                called.append(j)
                if j in eligible:
                    winner=j;break
                queue.remove(j);queue.append(j)
                events.append(dict(ciclo=k+1,data=now.isoformat(),docente=people[j].teacher.name,
                    evento='indisponivel_ao_ser_chamado_fim_da_fila'))
            if winner is not None:break
        assert len(called)==len(set(called))
        assert len(queue)==len(set(queue))
        sequence.append(people[winner].teacher.name if winner is not None else '-')
        before=queue.copy()
        for j,p in enumerate(people):
            t=p.teacher
            if j in eligible:
                participated[t.name]+=1
                rows.append(dict(ciclo=k+1,data=now.isoformat(),docente=t.name,base=float(base(t)),
                    posicao=queue.index(j)+1,aderencia=int(t.area),selecionado=int(j==winner)))
            if j==winner:
                counts[t.name]+=1;runs[t.name]+=1;maxrun=max(maxrun,runs[t.name]);losses[t.name]=0
                t.last_end=addmonths(now,interval)-timedelta(days=1)
                t.pending.append((t.last_end,F(60)))
            else:
                runs[t.name]=0
                if j in eligible:losses[t.name]+=1;maxwait=max(maxwait,losses[t.name])
        if winner is not None:
            queue.remove(winner);queue.append(winner)
            assert queue[:-1]==[j for j in before if j!=winner]
        else:assert queue==before
    return dict(politica='fila_assegurada',contagens={p.teacher.name:counts[p.teacher.name] for p in people},
        ofertas=len(dates),atribuicoes=sum(counts.values()),maior_sequencia=maxrun,maior_espera=maxwait,
        sem_atribuicao=sum(counts[n]==0 for n in participated),participacoes=dict(participated),sequencia=sequence,eventos=events),rows
