async def formatted_full_name(full_name: str) -> str:
    name_parts = full_name.split()
    last_name, first_name, middle_name = name_parts
    return f"{last_name} {first_name[0]}. {middle_name[0]}."
