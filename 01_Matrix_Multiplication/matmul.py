def matrix_multiply(matrix1, matrix2):
    # --- Validation of inputs ---
    
    # 1. Check if both inputs are lists (nested lists)
    if not isinstance(matrix1, list) or not isinstance(matrix2, list):
        raise ValueError("Both inputs must be nested lists representing matrices.")

    # 2. Check for empty matrices
    if not matrix1 or not matrix2:
        raise ValueError("Input matrices must not be empty.")

    # 3. Validate matrix1 rows (must all be lists of equal length)
    M = len(matrix1)  # rows in matrix1
    N1 = None
    for row in matrix1:
        if not isinstance(row, list):
            raise ValueError("Each row of matrix1 must be a list.")
        if N1 is None:
            N1 = len(row)  # set number of columns for matrix1
        elif len(row) != N1:
            raise ValueError("All rows in matrix1 must have the same number of columns.")

    # 4. Validate matrix2 rows (must all be lists of equal length)
    N2 = len(matrix2)  # rows in matrix2
    P = None
    for row in matrix2:
        if not isinstance(row, list):
            raise ValueError("Each row of matrix2 must be a list.")
        if P is None:
            P = len(row)  # set number of columns for matrix2
        elif len(row) != P:
            raise ValueError("All rows in matrix2 must have the same number of columns.")

    # 5. Check matrix dimensions (N1 == N2 required for multiplication)
    if N1 != N2:
        raise ValueError("Incompatible dimensions: "
                         f"matrix1 has {N1} columns, matrix2 has {N2} rows.")

    # --- Matrix multiplication ---
    
    result = []
    for i in range(M):  # for each row in matrix1
        row_result = []
        for j in range(P):  # for each column in matrix2
            product_sum = 0
            for k in range(N1):  # dot product of row i (matrix1) and col j (matrix2)
                a, b = matrix1[i][k], matrix2[k][j]
                if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                    raise TypeError("Matrix entries must be numeric (int or float).")
                product_sum += a * b
            row_result.append(product_sum)
        result.append(row_result)

    return result
