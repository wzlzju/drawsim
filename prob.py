def fac(n):
    if n <= 1:
        return 1
    pro = 1
    for i in range(1, n + 1):
        pro *= i
    return pro

def c(m, n):
    return fac(m) // fac(m - n) // fac(n)

def fi(N, n, M, m):
    if m > M:
        return 0
    return c(n, m) * c(N - n, M - m) / c(N, M)

def f(N, n, M, m):
    p = 0
    for i in range(m, n + 1):
        p += fi(N, n, M, i)
    return p

# N: deck num
# n: key num in deck
# M: hand num
# m: at least key num in hand