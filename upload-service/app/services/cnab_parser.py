"""CNAB fixed-width file parser."""


class CnabParser:
    def parse(self, content: bytes) -> list[dict]:
        lines = content.decode("utf-8", errors="replace").splitlines()
        transactions = []
        for line in lines:
            parsed = self.parse_line(line)
            if parsed is not None:
                transactions.append(parsed)
        return transactions

    def parse_line(self, line: str) -> dict | None:
        """Parses a single CNAB line. Returns None for empty or invalid lines.

        CNAB fixed-width layout (1-indexed):
          Type     : 1–1   (1 char)
          Date     : 2–9   (8 chars)  YYYYMMDD
          Amount   : 10–19 (10 chars) integer, divide by 100
          CPF      : 20–30 (11 chars)
          Card     : 31–42 (12 chars)
          Time     : 43–48 (6 chars)  HHMMSS
          Owner    : 49–62 (14 chars)
          Store    : 63–81 (19 chars)
        """
        stripped = line.rstrip("\n\r")
        if len(stripped) < 80:
            return None

        type_code_raw = stripped[0:1]
        date_raw = stripped[1:9]
        amount_raw = stripped[9:19]
        cpf_raw = stripped[19:30]
        card_raw = stripped[30:42]
        time_raw = stripped[42:48]
        owner_raw = stripped[48:62]
        store_raw = stripped[62:]

        try:
            type_code = int(type_code_raw)
        except ValueError:
            return None

        try:
            amount_cents = int(amount_raw)
        except ValueError:
            return None

        amount = f"{amount_cents / 100:.2f}"

        date = f"{date_raw[0:4]}-{date_raw[4:6]}-{date_raw[6:8]}"
        time = f"{time_raw[0:2]}:{time_raw[2:4]}:{time_raw[4:6]}"

        return {
            "type_code": type_code,
            "date": date,
            "amount": amount,
            "cpf": cpf_raw.strip(),
            "card": card_raw.strip(),
            "time": time,
            "store_owner": owner_raw.strip(),
            "store_name": store_raw.strip(),
        }
