def N_queen(n):
    board = [[' ' for _ in range(n)] for _ in range(n)]

    def safe_position(row, col):
        for i in range(col):
            if board[row][i] == 'Q':
                return False

        i, j = row, col
        while i >= 0 and j >= 0:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j -= 1

        i, j = row, col
        while i < n and j >= 0:
            if board[i][j] == 'Q':
                return False
            i += 1
            j -= 1

        return True

    def solve(col):
        if col >= n:
            return True

        for i in range(n):
            if safe_position(i, col):
                board[i][col] = 'Q'

                if solve(col + 1):
                    return True

                board[i][col] = ' '   

        return False

    if solve(0):
        horizontal_line = "+" + "---+" * n

        for i in range(n):
            print(horizontal_line)
            for j in range(n):
                print("|", end=" ")
                print(board[i][j], end=" ")
            print("|")
        print(horizontal_line)
    else:
        print("No solution exists")


n = int(input("Enter value of N: "))
N_queen(n)