from typing import List, Tuple

def read_chains(filename: str) -> List[List[Tuple[float, float]]]:
    chains = []
    points = []

    with open(filename) as f:
        for line in f:
            if not line.strip():
                continue
            if line.strip() == 'N':
                if points:
                    chains.append(points)
                    points = []
            else:
                x, y = map(float, line.strip().split(','))
                points.append((x, y))

        if points:
            chains.append(points)

    return chains
