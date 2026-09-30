"""Casos analíticos e invariantes do rodízio; somente dados fictícios."""
import unittest
from fila import queue_run
from modelo import Person, profile, START, addmonths, base
from cenarios import all_cases


class FilaTests(unittest.TestCase):
    def test_pontuacao(self):
        for points in [68, 80, 86, 100]:
            self.assertEqual(base(profile("A", points)), points)

    def test_equipes_estaveis(self):
        for n in [2, 5, 12]:
            result, _ = queue_run([Person(profile(f"P{j}", 100 if j == 0 else 68, True)) for j in range(n)])
            counts = result["contagens"].values()
            self.assertLessEqual(max(counts) - min(counts), 1)
            self.assertEqual(result["maior_sequencia"], 1)
            self.assertEqual(sum(counts), 40)

    def test_indisponibilidade_desloca_ao_fim(self):
        people = [Person(profile("A", 100)), Person(profile("B", 80)), Person(profile("C", 68))]
        people[0].absences = [(START, addmonths(START, 6))]
        result, _ = queue_run(people, years=2)
        self.assertEqual(result["sequencia"][:3], ["B", "C", "A"])
        self.assertEqual(result["eventos"][0]["docente"], "A")

    def test_ingressante_mais_pontuado_nao_ultrapassa(self):
        people = [Person(profile("A", 86)), Person(profile("B", 68)),
                  Person(profile("C", 100), entry=addmonths(START, 6))]
        result, _ = queue_run(people, years=2)
        self.assertEqual(result["sequencia"], ["A", "B", "A", "C"])

    def test_unico_disponivel_e_ninguem_disponivel(self):
        people = [Person(profile("A", 100)), Person(profile("B", 68),
                  absences=[(START, addmonths(START, 24))])]
        result, _ = queue_run(people, years=1)
        self.assertEqual(result["sequencia"], ["A", "A"])
        people[0].absences = [(START, addmonths(START, 24))]
        result, _ = queue_run(people, years=1)
        self.assertEqual(result["atribuicoes"], 0)
        self.assertEqual(len(result["eventos"]), 4)

    def test_precedencia_e_uso_da_subsidiaria(self):
        people = [Person(profile("A", 100)), Person(profile("B", 100))]
        people[0].teacher.area = False
        result, _ = queue_run(people, years=1)
        self.assertEqual(result["sequencia"], ["B", "B"])
        people[1].absences = [(START, addmonths(START, 24))]
        result, _ = queue_run(people, years=1)
        self.assertEqual(result["sequencia"], ["A", "A"])

    def test_crescimento_continuo(self):
        cases = all_cases()
        for rate, assignments, unserved in [(1, 4, 20), (2, 3, 53)]:
            result, _ = queue_run(cases[f"crescimento_{rate}_por_semestre_durante_39"])
            self.assertEqual(result["contagens"]["B"], assignments)
            self.assertEqual(result["sem_atribuicao"], unserved)
            self.assertEqual(result["sequencia"][1], "B")

    def test_conservacao_e_reprodutibilidade(self):
        for name, people in all_cases().items():
            kwargs = dict(period_change=name == "periodicidade_muda")
            result, rows = queue_run(people, **kwargs)
            self.assertEqual((result, rows), queue_run(people, **kwargs))
            self.assertEqual(sum(result["contagens"].values()), result["atribuicoes"])
            self.assertEqual(sum(r["selecionado"] for r in rows), result["atribuicoes"])
            self.assertLessEqual(result["atribuicoes"], result["ofertas"])


if __name__ == "__main__":
    unittest.main()
