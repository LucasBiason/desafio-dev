"""Generates a realistic CNAB test file with 20,000 lines.

Each store has a fixed owner and CPF. Transaction types follow a realistic
non-uniform distribution. Values vary per type to create interesting charts.
"""

import random
from datetime import date, timedelta

# Fixed store data: (store_name, owner_name, cpf)
# Store names are 19 chars padded, owner names are 14 chars padded
STORES = [
    ("BAR DO JOÃO       ", "JOÃO MACEDO   ", "09620676017"),
    ("LOJA DO Ó - MATRIZ", "MARIA JOSEFINA", "55641815063"),
    ("MERCADO DA AVENIDA", "MARCOS PEREIRA", "84515254073"),
    ("MERCEARIA 3 IRMÃOS", "JOSÉ COSTA    ", "23270298056"),
    ("LOJA DO Ó - FILIAL", "MARIA JOSEFINA", "55641815063"),
    ("PADARIA CENTRAL   ", "ANA OLIVEIRA  ", "12345678901"),
    ("FARMÁCIA SAÚDE    ", "CARLOS SOUZA  ", "98765432109"),
    ("RESTAURANTE SABOR ", "ELENA GOMES   ", "45678912345"),
    ("PET SHOP AMIGO    ", "BEATRIZ REIS  ", "78912345678"),
    ("AUTO PEÇAS SILVA  ", "RICARDO LIMA  ", "32165498700"),
]

# Transaction type distribution (type_code: weight)
# Types 1,2,3 are most common; 4,5,6,7,8,9 are less frequent
TYPE_WEIGHTS = {
    1: 25,   # Debito
    2: 20,   # Boleto
    3: 18,   # Financiamento
    4: 5,    # Credito
    5: 8,    # Recebimento Emprestimo
    6: 3,    # Vendas
    7: 7,    # Recebimento TED
    8: 10,   # Recebimento DOC
    9: 4,    # Aluguel
}

# Value ranges per type (min_cents, max_cents)
TYPE_VALUE_RANGES = {
    1: (500, 25000),       # Debito: R$ 5.00 - R$ 250.00
    2: (10000, 150000),    # Boleto: R$ 100.00 - R$ 1,500.00
    3: (50000, 500000),    # Financiamento: R$ 500.00 - R$ 5,000.00
    4: (1000, 80000),      # Credito: R$ 10.00 - R$ 800.00
    5: (100000, 1000000),  # Recebimento Emprestimo: R$ 1,000 - R$ 10,000
    6: (2000, 60000),      # Vendas: R$ 20.00 - R$ 600.00
    7: (5000, 300000),     # Recebimento TED: R$ 50.00 - R$ 3,000.00
    8: (3000, 200000),     # Recebimento DOC: R$ 30.00 - R$ 2,000.00
    9: (80000, 400000),    # Aluguel: R$ 800.00 - R$ 4,000.00
}

# Store activity weights (some stores are busier than others)
STORE_WEIGHTS = [15, 12, 18, 10, 8, 10, 7, 8, 6, 6]


def generate_card() -> str:
    """Generates a masked card number like 1234****5678."""
    first = f"{random.randint(1000, 9999)}"
    last = f"{random.randint(1000, 9999)}"
    return f"{first}****{last}"


def generate_time() -> str:
    """Generates a realistic time HHMMSS (business hours weighted)."""
    hour = random.choices(
        range(24),
        weights=[
            1, 0, 0, 0, 0, 0,    # 00-05
            2, 5, 10, 15, 18, 20,  # 06-11
            15, 18, 20, 18, 15, 12, # 12-17
            8, 5, 3, 2, 1, 1,     # 18-23
        ],
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}{minute:02d}{second:02d}"


def main():
    random.seed(42)

    # Date range: Jan 2025 - Dec 2025
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    date_range = (end_date - start_date).days

    type_codes = list(TYPE_WEIGHTS.keys())
    type_weights_list = list(TYPE_WEIGHTS.values())

    lines = []

    for _ in range(20000):
        # Pick store (weighted)
        store_idx = random.choices(range(len(STORES)), weights=STORE_WEIGHTS)[0]
        store_name, owner_name, cpf = STORES[store_idx]

        # Pick type (weighted)
        type_code = random.choices(type_codes, weights=type_weights_list)[0]

        # Pick value
        min_val, max_val = TYPE_VALUE_RANGES[type_code]
        amount = random.randint(min_val, max_val)

        # Pick date
        day_offset = random.randint(0, date_range)
        tx_date = start_date + timedelta(days=day_offset)
        date_str = tx_date.strftime("%Y%m%d")

        # Build line: type(1) + date(8) + amount(10) + cpf(11) + card(12) + time(6) + owner(14) + store(19) = 81 chars
        card = generate_card()
        time_str = generate_time()

        line = f"{type_code}{date_str}{amount:010d}{cpf}{card}{time_str}{owner_name}{store_name}"
        if len(line) != 80:
            raise ValueError(f"Line length {len(line)} (expected 80): {line!r}")
        lines.append(line)

    output_path = "/home/lucas-biason/Projetos/Projetos/Ativos/desafio-dev/assets/CNAB_BIG.txt"
    with open(output_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"Generated {len(lines)} lines to {output_path}")

    # Stats
    from collections import Counter
    type_counter = Counter()
    store_counter = Counter()
    for line in lines:
        type_counter[line[0]] += 1
        store_counter[line[62:]] += 1

    print("\nType distribution:")
    for tc, count in sorted(type_counter.items()):
        print(f"  Type {tc}: {count} ({count/len(lines)*100:.1f}%)")

    print(f"\nUnique stores: {len(store_counter)}")
    print("Store distribution:")
    for store, count in store_counter.most_common():
        print(f"  {store.strip()}: {count} ({count/len(lines)*100:.1f}%)")


if __name__ == "__main__":
    main()
