def create_text_file(filename: str = 'data.txt') -> str:
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(
            'username=SDET\npassword=secret_key'
        )
    return filename


def remove_text_file(filename: str = 'data.txt'):
    import os
    if os.path.exists(filename):
        os.remove(filename)
