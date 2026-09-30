"""Perfis fictícios, pontuação e calendário da simulação de rodízio."""
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction as F

START = date(2026, 1, 1)

def addmonths(d,n):
 y,m=divmod(d.year*12+d.month-1+n,12);m+=1
 return date(y,m,min(d.day,monthrange(y,m)[1]))

@dataclass
class Teacher:
 name:str
 level:int=20
 hours:F=F(360)
 days:F=F(720)
 area:bool=True
 last_end:date=None
 pending:list=field(default_factory=list)

def base(t,alt=False):
 return (60+t.level if t.area else 0)+(8 if alt else 12)*min(F(t.hours,360),1)+(12 if alt else 8)*min(F(t.days,720),1)

def profile(name,points,history=False):
 # Decomposição válida: menor nível que permite a base dada, com experiência limitada.
 level=next(x for x in [8,12,16,20] if points<=60+x+20)
 extra=points-60-level;h=min(extra,12)*30;days=max(extra-12,0)*90
 return Teacher(name,level,F(h),F(days),last_end=START-timedelta(days=1) if history else None)

@dataclass
class Person:
    teacher: object
    entry: date=START
    exit: date=date(2100,1,1)
    absences: list=field(default_factory=list)
    def can(self,when):
        return self.entry<=when<self.exit and not any(a<=when<b for a,b in self.absences)
