# this file was used to choose p and q values in generate_strategy() function, such that time of isogeny calculation
# is the lowest. It was used to precompute optimal strategies base_3_strat_SIDHp434 and base_2_strat_SIDHp434.

import random
import time

from src.sidh import choose_params, pari, isogeny_walk, generate_strategy, validate_strategy, exec_strategy, \
    encode_public_key, decode_public_key

times_2 = []
times_3 = []

def sidh_protocol(params_name, print_all, k_A, k_B, p_cost, q_cost, walk, cmp_strat):
    base_3_strat_SIDHp434 = [71, 34, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 17, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 38, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 21, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1]
    base_2_strat_SIDHp434 = [111, 58, 27, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 58, 27, 14, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 7, 4, 2, 1, 2, 1, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1]
    # ----------------- PUBLIC PARAMETERS SETUP -----------------
    params = choose_params(params_name)
    # params.print_params()


    # ----------------- ALICE's PUBLIC KEY GENERATION -----------------
    # print("-------------------------------------------------------------------")
    # print("------------------- ALICE's PUBLIC KEY GENERATION -----------------")
    # Alice chooses a secret in range <0, l_A ^ e_A>
    # k_A = 5  replaced outside function
    # print("k_A:", k_A)
    # Alice calculates secret generator corresponding to k_A
    k_AxQ_A = pari.ellmul(params.EC, params.Q_A, k_A)
    S_A = pari.elladd(params.EC, params.P_A, k_AxQ_A)
    # print(f"S_A: {S_A}")

    # Alice calculates isogeny path
    time1 = time.perf_counter()

    if walk == 'isogeny_walk':
        PK_A = isogeny_walk(2, S_A, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':
        if cmp_strat == True:
            strategy = generate_strategy(params.e_A, p_cost, q_cost)
            # validate_strategy(strategy)
        else:
            strategy = base_2_strat_SIDHp434
        PK_A = exec_strategy(params.EC, params.l_A, S_A, [params.P_B, params.Q_B], strategy, stage=1, x=params.Fp2_gen)

    time2 = time.perf_counter()
    time_elapsed = time2 - time1
    times_2.append(time_elapsed)
    # print(f'Time-2 elapsed: {time_elapsed}')

    # print(f'PK_A: {PK_A}')  # (EC', [P_B', Q_B'])

    # ----------------- BOB's PUBLIC KEY GENERATION -----------------
    # print("-------------------------------------------------------------------")
    # print("-------------------- BOB's PUBLIC KEY GENERATION ------------------")
    # Bob chooses a secret in range <0, l_B ^ e_B>
    # k_B = 9  # replaced outside function
    # print("k_B:", k_B)

    # Bob calculates secret generator corresponding to k_B
    k_BxQ_B = pari.ellmul(params.EC, params.Q_B, k_B)
    S_B = pari.elladd(params.EC, params.P_B, k_BxQ_B)
    # print(f"S_B: {S_B}")

    time1 = time.perf_counter()

    # Bob calculates isogeny path
    if walk == 'isogeny_walk':
        PK_B = isogeny_walk(3, S_B, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':
        if cmp_strat == True:
            strategy = generate_strategy(params.e_B, p_cost, q_cost)
            # validate_strategy(strategy)
        else:
            strategy = base_3_strat_SIDHp434
        PK_B = exec_strategy(params.EC, params.l_B, S_B, [params.P_A, params.Q_A], strategy, stage=1, x=params.Fp2_gen)
    # print(f'PK_B: {PK_B}')  # (EC', [P_A', Q_A'])

    time2 = time.perf_counter()
    time_elapsed = time2 - time1
    times_3.append(time_elapsed)
    # print(f'Time-3 elapsed: {time_elapsed}')


    # ----------------- ALICE's SHARED KEY COMPUTATION -----------------
    # print("--------------------------------------------------------------------")
    # print("----------------- ALICE's SHARED KEY COMPUTATION -----------------")
    EC_from_PK_B = PK_B[0]

    # Alice calculates secret generator on Elliptic curve from Bob's public key corresponding to k_A
    k_AxQ_A = pari.ellmul(EC_from_PK_B, PK_B[1][1], k_A)
    S_A = pari.elladd(EC_from_PK_B, PK_B[1][0], k_AxQ_A)
    # print(f"S_A: {S_A}")

    time1 = time.perf_counter()

    # Alice calculates isogeny path
    if walk == 'isogeny_walk':
        SK_A = isogeny_walk(2, S_A, params, stage=2, EC_from_PK=EC_from_PK_B, print_all=print_all)
    elif walk == 'optimal_strategy':
        if cmp_strat == True:
            strategy = generate_strategy(params.e_A, p_cost, q_cost)
            # validate_strategy(strategy)
        else:
            strategy = base_2_strat_SIDHp434
        SK_A = exec_strategy(EC_from_PK_B, params.l_A, S_A, [], strategy, stage=2, x=params.Fp2_gen)[0]
    # SK_A = SK_A.j()
    # print("ALICE's SECRET:", SK_A)

    time2 = time.perf_counter()
    time_elapsed = time2 - time1
    times_2.append(time_elapsed)
    # print(f'Time-2 elapsed: {time_elapsed}')

    # ----------------- BOB's SHARED KEY COMPUTATION -----------------
    # print("------------------------------------------------------------------")
    # print("----------------- BOB's SHARED KEY COMPUTATION -----------------")
    EC_from_PK_A = PK_A[0]

    # Bob calculates secret generator on Elliptic curve from Bob's public key corresponding to k_A
    k_BxQ_B = pari.ellmul(EC_from_PK_A, PK_A[1][1], k_B)
    S_B = pari.elladd(EC_from_PK_A, PK_A[1][0], k_BxQ_B)
    # print(f"S_B: {S_B}")

    time1 = time.perf_counter()

    # Bob calculates isogeny path
    if walk == 'isogeny_walk':
        SK_B = isogeny_walk(3, S_B, params, stage=2, EC_from_PK=EC_from_PK_A, print_all=print_all)
    elif walk == 'optimal_strategy':
        if cmp_strat == True:
            strategy = generate_strategy(params.e_B, p_cost, q_cost)
            # validate_strategy(strategy)
        else:
            strategy = base_3_strat_SIDHp434
        SK_B = exec_strategy(EC_from_PK_A, params.l_B, S_B, [], strategy, stage=2, x=params.Fp2_gen)[0]
    # SK_B = SK_B.j()
    # print("BOB's SECRET:", SK_B)

    time2 = time.perf_counter()
    time_elapsed = time2 - time1
    times_3.append(time_elapsed)
    # print(f'Time-3 elapsed: {time_elapsed}')

    # print("---------------------CHECK---------------------")
    # print("ALICE's SECRET:", SK_A)
    # print("BOB's SECRET:", SK_B)


def main():
    # print('imports loaded, starting main...')
    max_range_1 = 11  # range checked
    max_range_2 = 3  # number of executions, to get more accurate average
    for i in range(0, max_range_1):
        p_cost = 100  # 100
        q_cost = 50 + i * 10  # 120

        for j in range(0, max_range_2):
            config = {
                'params_name': "SIKEp434",  # 'small' 'medium' 'SIKEp434'
                'print_all': False,  # True False (for visualiation when using 'small' params)
                'k_A': random.randint(1, pow(2, 216)),  # Alice chooses a secret
                'k_B': random.randint(1, pow(3, 137)),  # Bob chooses a secret
                'p_cost': p_cost,  # multiplication cost for optimal_strategy
                'q_cost': q_cost,  # isogeny cost for optimal_strategy
                'walk': 'optimal_strategy',  # 'isogeny_walk' 'optimal_strategy'
                'cmp_strat': True,  # False
            }
            sidh_protocol(**config)

        print('--------------------------------------------')
        print(f'{max_range_2} executions, p_cost={p_cost}, q_cost={q_cost}:')
        print(f'times_2 average:{sum(times_2)/len(times_2)}')
        print(f'times_3 average:{sum(times_3)/len(times_3)}')

        '''
        The lowest computation times were achieved with p_cost = 100 and q_cost = 120
        The strategies are the follwoing:
        base_3_strat_SIDHp434 = [71, 34, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 17, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 38, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 21, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1]
        base_2_strat_SIDHp434 = [111, 58, 27, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 58, 27, 14, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 7, 4, 2, 1, 2, 1, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1]

        '''


if __name__ == "__main__":
    main()

