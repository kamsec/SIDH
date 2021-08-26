# this file shows example execution of a protocol on single machine


import time
import random
from src.sidh import choose_params, pari, isogeny_walk, generate_strategy, validate_strategy, exec_strategy,\
    encode_public_key, decode_public_key

# precomputed best strategies for isogeny computations (using file sidh_isogeny_benchmark)
base_3_strat_SIDHp434 = [71, 34, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3,
                         1, 2, 1, 17, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1,
                         1, 3, 1, 2, 1, 38, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5,
                         2, 1, 1, 3, 1, 2, 1, 21, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 12, 5, 2, 1, 1, 3, 1,
                         2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1]
base_2_strat_SIDHp434 = [111, 58, 27, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4,
                         2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1,
                         1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8,
                         4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 58, 27, 14, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 7, 4, 2,
                         1, 2, 1, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2,
                         1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1,
                         1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1]


def sidh_protocol(params_name, print_all, k_A, k_B, p_cost, q_cost, walk):
    # ----------------- PUBLIC PARAMETERS SETUP -----------------
    params = choose_params(params_name)
    params.print_params()

    # ----------------- ALICE's PUBLIC KEY GENERATION -----------------
    print("-------------------------------------------------------------------")
    print("------------------- ALICE's PUBLIC KEY GENERATION -----------------")
    # Alice chooses a secret in range <0, l_A ^ e_A>
    k_A = random.randint(1, pow(2, 216))
    print("k_A:", k_A)
    # Alice calculates secret generator corresponding to k_A
    k_AxQ_A = pari.ellmul(params.EC, params.Q_A, k_A)
    S_A = pari.elladd(params.EC, params.P_A, k_AxQ_A)
    print(f"S_A: {S_A}")

    # Alice calculates isogeny path
    if walk == 'isogeny_walk':  # slow, isogeny as composition of 2-isogenies
        PK_A = isogeny_walk(2, S_A, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':  # fast, isogeny as composition of different degree isogenies with optimal strategy
        # strategy = generate_strategy(params.e_A, p_cost, q_cost)  # strategy computation on runtime
        # validate_strategy(strategy) # we can quickly check if strategy is valid
        strategy = base_2_strat_SIDHp434  # using precomputed strategy
        PK_A = exec_strategy(params.EC, params.l_A, S_A, [params.P_B, params.Q_B], strategy, stage=1, x=params.Fp2_gen)
    print(f'PK_A: {PK_A}')  # (EC', [P_B', Q_B'])
    # Because it is designed to run on a single machine, public keys are not encoded here

    # ----------------- BOB's PUBLIC KEY GENERATION -----------------
    print("-------------------------------------------------------------------")
    print("-------------------- BOB's PUBLIC KEY GENERATION ------------------")
    # Bob chooses a secret in range <0, l_B ^ e_B>
    k_B = random.randint(1, pow(3, 137))
    print("k_B:", k_B)

    # Bob calculates secret generator corresponding to k_B
    k_BxQ_B = pari.ellmul(params.EC, params.Q_B, k_B)
    S_B = pari.elladd(params.EC, params.P_B, k_BxQ_B)
    print(f"S_B: {S_B}")

    # Bob calculates isogeny path
    if walk == 'isogeny_walk':
        PK_B = isogeny_walk(3, S_B, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':
        # strategy = generate_strategy(params.e_B, p_cost, q_cost)
        # validate_strategy(strategy)
        strategy = base_3_strat_SIDHp434
        PK_B = exec_strategy(params.EC, params.l_B, S_B, [params.P_A, params.Q_A], strategy, stage=1, x=params.Fp2_gen)
    print(f'PK_B: {PK_B}')  # (EC', [P_A', Q_A'])

    # ----------------- ALICE's SHARED KEY COMPUTATION -----------------
    print("-------------------------------------------------------------------")
    print("------------------ ALICE's SHARED KEY COMPUTATION -----------------")
    EC_from_PK_B = PK_B[0]

    # Alice calculates secret generator on Elliptic curve from Bob's public key corresponding to k_A
    k_AxQ_A = pari.ellmul(EC_from_PK_B, PK_B[1][1], k_A)
    S_A = pari.elladd(EC_from_PK_B, PK_B[1][0], k_AxQ_A)
    print(f"S_A: {S_A}")

    # Alice calculates isogeny path
    if walk == 'isogeny_walk':
        SK_A = isogeny_walk(2, S_A, params, stage=2, EC_from_PK=EC_from_PK_B, print_all=print_all)
    elif walk == 'optimal_strategy':
        # strategy = generate_strategy(params.e_A, p_cost, q_cost)
        # validate_strategy(strategy)
        strategy = base_2_strat_SIDHp434
        SK_A = exec_strategy(EC_from_PK_B, params.l_A, S_A, [], strategy, stage=2, x=params.Fp2_gen)[0]
    SK_A = str(SK_A.j())
    print("ALICE's SECRET:", SK_A)

    # ----------------- BOB's SHARED KEY COMPUTATION -----------------
    print("-------------------------------------------------------------------")
    print("------------------- BOB's SHARED KEY COMPUTATION ------------------")
    EC_from_PK_A = PK_A[0]

    # Bob calculates secret generator on Elliptic curve from Bob's public key corresponding to k_A
    k_BxQ_B = pari.ellmul(EC_from_PK_A, PK_A[1][1], k_B)
    S_B = pari.elladd(EC_from_PK_A, PK_A[1][0], k_BxQ_B)
    print(f"S_B: {S_B}")

    # Bob calculates isogeny path
    if walk == 'isogeny_walk':
        SK_B = isogeny_walk(3, S_B, params, stage=2, EC_from_PK=EC_from_PK_A, print_all=print_all)
    elif walk == 'optimal_strategy':
        # strategy = generate_strategy(params.e_B, p_cost, q_cost)
        # validate_strategy(strategy)
        strategy = base_3_strat_SIDHp434
        SK_B = exec_strategy(EC_from_PK_A, params.l_B, S_B, [], strategy, stage=2, x=params.Fp2_gen)[0]
    SK_B = str(SK_B.j())
    print("BOB's SECRET:", SK_B)

    print("------------------------------ CHECK ------------------------------")
    if SK_A == SK_B:
        print("Success! SHARED KEY =", SK_A)
    else:
        print("Keys are different. Something went wrong :(")


def main():
    config = {
        'params_name': "SIKEp434",  # 'small' 'medium' 'SIKEp434'
        'print_all': False,  # True False (for visualiation when using 'small' params)
        'k_A': None,  # Alice chooses a secret - inside the function
        'k_B': None,  # Bob chooses a secret - inside the function
        'p_cost': 100,  # multiplication cost for optimal_strategy - uses precomputed value
        'q_cost': 120,  # isogeny cost for optimal_strategy - uses precomputed value
        'walk': 'optimal_strategy',  # 'isogeny_walk' 'optimal_strategy'
    }
    sidh_protocol(**config)


if __name__ == "__main__":
    time1 = time.perf_counter()
    main()
    time2 = time.perf_counter()
    print(f'Time elapsed: {time2 - time1}')
