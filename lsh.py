import asyncio
import itertools
from multiprocessing import Pool

from datasketch.experimental.aio.lsh import AsyncMinHashLSH
from datasketch import MinHash
import codecs


def next_key():
    with codecs.open('labels.txt', 'r', "utf-8") as file:
        last_key = None
        data = set()
        ll = 0
        for line in file:
            record = line.split(':', 1)
            if int(record[0][1:]) < 0:
                continue
            else:
                if int(record[0][1:]) > ll + 10000:
                    ll = int(record[0][1:])
                    print(record[0])

            if record[0] == last_key:
                data.update(record[1].lower().split())
            else:
                if len(data) > 0:
                    yield last_key, data

                last_key = record[0]
                data = set(record[1].lower().split())


def next_real_key(p):
    mh = MinHash(num_perm=256)
    key, data = p
    for d in data:
        mh.update(d.encode('utf8'))

    return key, mh


async def func():
    async with AsyncMinHashLSH(threshold=0.3, num_perm=256, storage_config={
        'type': 'aiomongo',
        'basename': 'k'.encode('utf8'),
        'mongo': {'host': 'localhost', 'port': 27017, 'db': 'lsh'}
    }) as lsh:
        with codecs.open('dataset.csv', 'r', "utf-8") as file:
            for line in file:
                record = line.split(',', 1)
                test = record[0].lower().split()
                mh = MinHash(num_perm=256)
                for d in test:
                    mh.update(d.encode('utf8'))
                result = await lsh.query(mh)
                print(record[0], record[1], result)



async def queries():
    async with AsyncMinHashLSH(threshold=0.01, num_perm=256, storage_config={
        'type': 'aiomongo',
        'basename': 'k'.encode('utf8'),
        'mongo': {'host': 'localhost', 'port': 27017, 'db': 'lsh'}
    }) as lsh:

        async with lsh.insertion_session(batch_size=1000) as session:
            pool = Pool(6)
            keys = next_key()

            res = [x for x in pool.map(next_real_key, itertools.islice(keys, 1000))]
            while res:
                fs = (session.insert(key, minhash, check_duplication=False) for key, minhash in res)
                res = [x for x in pool.map(next_real_key, itertools.islice(keys, 1000))]
                await asyncio.gather(*fs)

            pool.close()
            pool.join()


if __name__ == '__main__':
    asyncio.run(func())
