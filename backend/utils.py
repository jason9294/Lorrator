def foo(x, y):
    return x + y


def sum(*args):
    total = 0
    for value in args:
        total += value
    return total


def bubble_sort(arr):
    result = list(arr)
    n = len(result)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break

    return result
