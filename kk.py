import requests

def print_secret_message(doc_url: str):
    """
    Fetches a Google Doc containing x, y coordinates and Unicode characters,
    builds the grid, and prints the resulting message.
    """

    # Fetch document content
    response = requests.get(doc_url)
    response.raise_for_status()
    text = response.text

    points = []

    # Split into lines and try to extract valid rows
    for line in text.splitlines():
        parts = line.strip().split()

        # Expect format: x-coordinate, character, y-coordinate
        if len(parts) >= 3:
            try:
                x = int(parts[0])
                char = parts[1]
                y = int(parts[2])
                points.append((x, y, char))
            except ValueError:
                continue  # skip headers or invalid rows

    if not points:
        print("")
        return

    # Determine grid size
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)

    # Create empty grid filled with spaces
    grid = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    # Fill grid with characters
    for x, y, char in points:
        grid[y][x] = char

    # Print grid (y=0 at top, increasing downward)
    for row in grid:
        print("".join(row))
        
print_secret_message("https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub")