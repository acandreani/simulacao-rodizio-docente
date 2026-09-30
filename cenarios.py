"""Vinte e um cenários sintéticos; nenhuma pessoa ou cadastro real."""
from datetime import date
from modelo import Person, profile, START, addmonths

def case(n):return [Person(profile(chr(65+j),100-2*j,j==0)) for j in range(n)]

def scenarios():
    out={'dois_100_68':[Person(profile('A',100,True)),Person(profile('B',68))],
         'cinco_estaveis':case(5),'doze_estaveis':case(12)}
    p=case(5)
    for x in p[2:]:x.entry=date(2032,1,1)
    out['entrada_janeiro_2_para_5']=p
    p=case(5)
    for x in p[2:]:x.entry=date(2032,7,1)
    out['entrada_julho_2_para_5']=p
    p=case(12)
    for x in p[2:]:x.exit=date(2032,1,1)
    out['saida_12_para_2']=p
    p=case(12)
    for x in p[2:]:x.exit=date(2027,1,1)
    out['saida_precoce_12_para_2']=p
    p=case(5)
    for x in p[2:]:x.exit=date(2032,7,1)
    out['saida_julho_5_para_2']=p
    p=case(5)
    for x in p[2:]:x.absences=[(date(2032,1,1),date(2035,1,1))]
    out['afastamento_tres_anos']=p
    p=case(5);p[1].absences=[(date(2032,7,1),date(2033,1,1))]
    out['afastamento_um_semestre']=p
    p=case(2);p[1].exit=date(2032,1,1)
    out['resta_um_docente']=p
    out['periodicidade_muda']=case(5)
    return out

def all_cases():
    cases=scenarios()
    for rate in [1,2]:
        for stop in [4,12,39]:
            p=[Person(profile('A',100,True)),Person(profile('B',68,True))]
            for k in range(1,stop+1):
                for j in range(rate):p.append(Person(profile(f'E{k:02}_{j}',68),entry=addmonths(START,6*k)))
            cases[f'crescimento_{rate}_por_semestre_durante_{stop}']=p
    for n in [2,5,12]:
        cases[f'historico_recente_todos_{n}']=[Person(profile(f'P{j+1}',100 if j==0 else 68,True)) for j in range(n)]
    return cases
