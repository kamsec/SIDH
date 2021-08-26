# this file is client-side implementation on a weaker machine,
# Raspberry Pi Zero W with 512MB RAM and 1x 1GHz processor
# benchmarks showed that base 3 isogenies are less time consuming, so client will only play a role of Bob (3-isogeny)

import asyncio
import random
import time
from src.sidh import choose_params, pari, isogeny_walk, generate_strategy, validate_strategy, exec_strategy, \
    encode_public_key, decode_public_key


base_3_strat_SIDHp434 = [71, 34, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3,
                         1, 2, 1, 17, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1,
                         1, 3, 1, 2, 1, 38, 17, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 9, 4, 2, 1, 1, 2, 1, 1, 5,
                         2, 1, 1, 3, 1, 2, 1, 21, 9, 4, 2, 1, 1, 2, 1, 1, 5, 2, 1, 1, 3, 1, 2, 1, 12, 5, 2, 1, 1, 3, 1,
                         2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1]


# side='BOB' is obligatory for this implementation, other parameters can be changed
async def sidh(params_name='SIKEp434', walk='optimal_strategy', side='BOB', print_all=False):
    time0 = time.perf_counter()

    reader, writer = await asyncio.open_connection(
        '192.168.0.101', 1234)

    params = choose_params(params_name)

    # if walk is 'optimal_strategy' and params = SIKEp434, precomputed strategy can be used, otherwise we compute it
    # if walk is 'isogeny_walk', strategy won't be set and isogeny is computed in non-optimized way
    if (walk == 'optimal_strategy') and (params_name == 'SIKEp434'):
        strategy = base_3_strat_SIDHp434
    elif (walk == 'optimal_strategy') and ((params_name == 'small') or (params_name == 'medium')):
        strategy = generate_strategy(params.e_B, 100, 120)
        validate_strategy(strategy)

    k_B = random.randint(1, pow(3, 137))
    k_BxQ_B = pari.ellmul(params.EC, params.Q_B, k_B)
    S_B = pari.elladd(params.EC, params.P_B, k_BxQ_B)

    if walk == 'isogeny_walk':
        PK_B = isogeny_walk(3, S_B, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':
        PK_B = exec_strategy(params.EC, params.l_B, S_B, [params.P_A, params.Q_A], strategy, stage=1, x=params.Fp2_gen)
    # PK_B = [EC', [P_A', Q_A']]
    PK_B_encoded = encode_public_key(*PK_B, params_name, side)

    print(f'CLIENT -> SERVER: {PK_B_encoded}')
    writer.write(PK_B_encoded.encode())
    writer.write_eof()
    await writer.drain()

    PK_A_received = await reader.read()  # bytes
    PK_A_string = PK_A_received.decode()  # string
    PK_A = decode_public_key(PK_A_received)  # [EC, [P,Q]]
    print(f'SERVER -> CLIENT: {PK_A_string}')

    EC_from_PK_A = PK_A[0]
    k_BxQ_B = pari.ellmul(EC_from_PK_A, PK_A[1][1], k_B)
    S_B = pari.elladd(EC_from_PK_A, PK_A[1][0], k_BxQ_B)

    if walk == 'isogeny_walk':
        SK_B = isogeny_walk(3, S_B, params, stage=2, EC_from_PK=EC_from_PK_A, print_all=print_all)
    elif walk == 'optimal_strategy':
        SK_B = exec_strategy(EC_from_PK_A, params.l_B, S_B, [], strategy, stage=2, x=params.Fp2_gen)[0]
    SK_B = str(SK_B.j())
    SK_B = SK_B.replace('*', '').replace('i', '').replace(' ', '').replace('+', '')
    print("BOB's SECRET:", SK_B)

    print('Close the connection')
    writer.close()
    time1 = time.perf_counter()
    print(f'Time elapsed: {time1 - time0}')

asyncio.run(sidh())
