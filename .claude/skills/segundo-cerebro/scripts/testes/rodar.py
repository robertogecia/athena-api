#!/usr/bin/env python3
"""Roda o lint contra os casos de regressão e compara com esperado.txt.

    python3 testes/rodar.py

Sai 0 se tudo bate, 1 se algum caso divergiu. A data é fixada em 2026-09-08
para que "há mais de 6 meses" não mude de resposta com o passar do tempo.
"""
import collections, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(os.path.dirname(AQUI), "lint.py")
HOJE = "2026-09-08"


def rotulos(saida):
    achados = re.findall(r"^\[([A-Z?-]+)\]", saida, re.MULTILINE)
    return dict(collections.Counter(achados))


def main():
    falhas = 0
    with open(os.path.join(AQUI, "esperado.txt"), encoding="utf-8") as fh:
        linhas = [l for l in fh if l.strip() and not l.startswith("#")]

    for linha in linhas:
        nome, cod_esp, rot_esp = (linha.rstrip("\n").split("|") + ["", ""])[:3]
        esperado = {}
        for par in rot_esp.split():
            chave, _, n = par.rpartition(":")
            esperado[chave] = int(n)

        proc = subprocess.run(
            [sys.executable, LINT, "--base", os.path.join(AQUI, "casos", nome),
             "--hoje", HOJE],
            capture_output=True, text=True)
        obtido = rotulos(proc.stdout)

        problemas = []
        if proc.returncode != int(cod_esp):
            problemas.append(f"saída {proc.returncode}, esperava {cod_esp}")
        if obtido != esperado:
            problemas.append(f"rótulos {obtido or '{}'}, esperava {esperado or '{}'}")
        if "Traceback" in proc.stderr:
            problemas.append("estourou: " + proc.stderr.strip().splitlines()[-1])

        if problemas:
            falhas += 1
            print(f"FALHA  {nome}")
            for p in problemas:
                print(f"       {p}")
        else:
            print(f"ok     {nome}")

    print(f"\n{len(linhas) - falhas}/{len(linhas)} casos passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
