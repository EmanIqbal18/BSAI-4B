#Water Jug using DFS
def water_jug_dfs(jug_A, jug_B, target):

    visited = set()

    def dfs(x, y, path):

        if (x, y) in visited:
            return None

        visited.add((x, y))

        if x == target or y == target:
            return path

        actions = [
            ((jug_A, y), "Fill A"),
            ((x, jug_B), "Fill B"),
            ((0, y), "Empty A"),
            ((x, 0), "Empty B"),
            ((x - min(x, jug_B - y), y + min(x, jug_B - y)), "Pour A in B"),
            ((x + min(y, jug_A - x), y - min(y, jug_A - x)), "Pour B in A"),
        ]

        for (nx, ny), rule in actions:
            result = dfs(nx, ny, path + [f"{rule} ({nx},{ny})"])
            if result:
                return result

        return None

    return dfs(0, 0, [])


# Example
jug_A = 3
jug_B = 4
target = 2

solution = water_jug_dfs(jug_A, jug_B, target)

if solution:
    print("Steps:")
    for step in solution:
        print(step)
else:
    print("No solution found.")