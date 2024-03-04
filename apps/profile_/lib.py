from apps.shared import ui, renders


ui = ui
renders = renders


def half_hidden(
    line: str,
    number_of_not_hidden: int,
    *,
    hidden_symbol: str = '#',
) -> str:
    if len(line) < number_of_not_hidden * 2:
        return hidden_symbol * len(line)

    start = line[:number_of_not_hidden]
    middle = hidden_symbol * (len(line) - number_of_not_hidden * 2)
    end = line[-number_of_not_hidden:]

    return start + middle + end
