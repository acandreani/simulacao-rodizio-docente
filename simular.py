"""Executa os 121 casos da fila e grava resultados reproduzíveis."""
import argparse
import csv
import json
import random
from datetime import date
from pathlib import Path
from cenarios import all_cases
from fila import queue_run
from modelo import Person, profile


def writecsv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=Path("resultados"))
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    results, memory, sensitivity = [], [], []
    for name, people in all_cases().items():
        result, rows = queue_run(people, period_change=name == "periodicidade_muda")
        result["cenario"] = name
        results.append(result)
        for row in rows:
            row["cenario"] = name
        memory.extend(rows)
    for n in [2, 3, 5, 9, 12]:
        for rep in range(20):
            seed = 20261001 + n * 1000 + rep
            rng = random.Random(seed)
            people = [Person(profile(f"P{j}", rng.choice([68, 80, 86, 100]), True)) for j in range(n)]
            for person in people:
                if rng.random() < .35:
                    person.absences = [(date(2032, 1, 1), date(2034, 1, 1))]
            result, _ = queue_run(people, seed=seed, interest=.8)
            sensitivity.append(dict(n=n, rep=rep, seed=seed, **{
                k: v for k, v in result.items() if not isinstance(v, (list, dict))
            }))
    (args.saida / "resultados.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    writecsv(args.saida / "memoria_fila.csv", memory)
    writecsv(args.saida / "sensibilidade.csv", sensitivity)
    (args.saida / "execucao.json").write_text(json.dumps(dict(
        cenarios=21, equipes_sensibilidade=100, execucoes=121, anos=20,
        dados="inteiramente sinteticos", politica="fila_assegurada",
        semente_cenarios=1, semente_sensibilidade="20261001 + n * 1000 + rep"
    ), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Concluídas 121 execuções. Resultados em {args.saida}")


if __name__ == "__main__":
    main()
