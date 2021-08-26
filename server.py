# this file is server-side implementation on a stronger machine,
# laptop with 8Gb RAM and 4x 2.3GHz processor
# benchmarks showed that base 2 isogenies are more time consuming, so server will only play a role of Alice (2-isogeny)

import asyncio
import random
import time
from json import loads
from src.sidh import choose_params, pari, isogeny_walk, generate_strategy, validate_strategy, exec_strategy,\
    encode_public_key, decode_public_key

IP = '0.0.0.0'
PORT = 1234


base_2_strat_SIDHp434 = [111, 58, 27, 12, 5, 2, 1, 1, 3, 1, 2, 1, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4,
                         2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1,
                         1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8,
                         4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 58, 27, 14, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 7, 4, 2,
                         1, 2, 1, 1, 4, 2, 1, 2, 1, 1, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2,
                         1, 1, 2, 1, 1, 31, 15, 7, 3, 1, 2, 1, 4, 2, 1, 2, 1, 1, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1,
                         1, 16, 8, 4, 2, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1, 8, 4, 2, 1, 1, 2, 1, 1, 4, 2, 1, 1, 2, 1, 1]

# side='ALICE' is obligatory for this implementation, other parameters can be changed
async def handle_client(reader, writer, walk='optimal_strategy', side='ALICE', print_all=False):
    time0 = time.perf_counter()
    PK_B_received = await reader.read()  # bytes
    PK_B_string = PK_B_received.decode()  # string
    PK_B = decode_public_key(PK_B_received)  # [EC, [P,Q]]
    print(f"CLIENT -> SERVER: {PK_B_string}")

    params_name = loads(PK_B_string)['protocol']['params']
    params = choose_params(params_name)

    # if walk is 'optimal_strategy' and params = SIKEp434, precomputed strategy can be used, otherwise we compute it
    # if walk is 'isogeny_walk', strategy won't be set and isogeny is computed in non-optimized way
    if (walk == 'optimal_strategy') and (params_name == 'SIKEp434'):
        strategy = base_2_strat_SIDHp434
    elif (walk == 'optimal_strategy') and ((params_name == 'small') or (params_name == 'medium')):
        strategy = generate_strategy(params.e_A, 100, 120)
        validate_strategy(strategy)

    k_A = random.randint(1, pow(2, 216))
    k_AxQ_A = pari.ellmul(params.EC, params.Q_A, k_A)
    S_A = pari.elladd(params.EC, params.P_A, k_AxQ_A)

    if walk == 'isogeny_walk':
        PK_A = isogeny_walk(2, S_A, params, stage=1, print_all=print_all)
    elif walk == 'optimal_strategy':
        PK_A = exec_strategy(params.EC, params.l_A, S_A, [params.P_B, params.Q_B], strategy, stage=1, x=params.Fp2_gen)
    # PK_A = [EC', [P_B', Q_B']]
    PK_A_encoded = encode_public_key(*PK_A, params_name, side)
    print(f"SERVER -> CLIENT: {PK_A_encoded}")
    writer.write(PK_A_encoded.encode())
    writer.write_eof()
    await writer.drain()

    EC_from_PK_B = PK_B[0]
    k_AxQ_A = pari.ellmul(EC_from_PK_B, PK_B[1][1], k_A)
    S_A = pari.elladd(EC_from_PK_B, PK_B[1][0], k_AxQ_A)
    if walk == 'isogeny_walk':
        SK_A = isogeny_walk(2, S_A, params, stage=2, EC_from_PK=EC_from_PK_B, print_all=print_all)
    elif walk == 'optimal_strategy':
        SK_A = exec_strategy(EC_from_PK_B, params.l_A, S_A, [], strategy, stage=2, x=params.Fp2_gen)[0]
    SK_A = str(SK_A.j())
    SK_A = SK_A.replace('*', '').replace('i', '').replace(' ', '').replace('+', '')
    print("ALICE's SECRET:", SK_A)

    print("Close the connection")
    writer.close()
    time1 = time.perf_counter()
    print(f'Time elapsed: {time1 - time0}')

async def main():
    server = await asyncio.start_server(handle_client, IP, PORT)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
