import random


class RandomIterator:
    value = 0

    def __init__(self):
        self.value = random.randint(100, 10000000)

    def __call__(self, *args, **kwargs):
        increase = random.randint(60, 5000)

        self.value += increase

        return self.value, increase


def weightedRandom(max=2, startZeros=4, otherInts=3):
    arr = [0 for _ in range(startZeros)]

    for _ in range(otherInts):
        arr.append(random.randint(1, max))

    return random.choice(arr)

randIt = RandomIterator()

with open('test_cases/test5.ags', 'w+') as f:
    f.write('expname imgfile timfile blocknr subjectnr pagenr samplenr samstart event fixnr fixdur qual obtnr oldobtnr'
            ' code code2 timcode timstart timname\n')

    possible_codes = [random.randint(0, 40) for _ in range(6)]
    possible_codes2 = [random.randint(0, 40) for _ in range(6)]
    timstarts = ['Hee', 'Hoo', 'Haa', 'Hihi', 'Heyo', 'Meep']

    for pagenr, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']):
        pagenr_c = random.randint(0, 60)
        fixnr = random.randint(0,3)
        fixdur = random.randint(100, 3000)
        qual = random.randint(1, 3)
        obtnr = random.randint(1, 10)
        oldobtnr = random.randint(1, 200)
        code = random.choice(possible_codes)
        for i, possible_code2 in enumerate(possible_codes2):
            string = timstarts[i]
            for stim_num in range(200):
                stim_id = '{0}{1:0>3}.BMP'.format(letter, pagenr)

                f.write(
                    "TST {}  11 0 {} {} {} F {} {} {} {} {} 0 {} {} {} \n".format(
                        stim_id,
                        pagenr,
                        stim_num,
                        randIt()[0],
                        fixnr,
                        fixdur,
                        qual,
                        obtnr,
                        oldobtnr,
                        code,
                        possible_code2,
                        string
                    )
                )


exit()

with open('test_cases/test5.JNF', 'w+') as f:
    f.write('expname imgfile timfile blocknr subjectnr pagenr fixnr X Y fixstart fixdur SaccInDur SaccOutDur Qual Mark '
            'obtnr oldobtnr wlen nwonl twonl ncharl nwonp nline tlines pagenr left top right bottom code code2 timcode '
            'timstart timname shiftx shifty\n')
    with open('test_cases/test6.agc', 'w+') as f2:
        f2.write('expname blocknr subjectnr imgfile pagenr code code2 ffdur ffqual ffbck ffin ffout rpdur rpqual rpcnt '
                 'rpsacc rpout tgdur tgqual tgcnt tgsacc tgout gdur gqual gcnt gsacc gbck gout\n')

        possible_codes = [random.randint(0, 40) for _ in range(6)]
        possible_codes2 = [random.randint(0, 40) for _ in range(6)]

        for pagenr, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']):
            pagenr_c = random.randint(0, 60)
            for stim_num in range(10):
                stim_id = '{0}{1:0>3}.BMP'.format(letter, pagenr)

                blocknr = 11
                subjectnr = 1
                X = random.randint(1, 800)
                Y = random.randint(1, 500)

                fixstart, fixdur = randIt()
                fixdur = random.randint(60, fixdur)

                saccindur = weightedRandom(600, 3, 9)
                saccoutdur = weightedRandom(600, 3, 9)

                qual = weightedRandom()
                mark = weightedRandom(4)
                obtnr = weightedRandom(9, 3, 9)

                wlen = random.randint(0, 15)
                nwonl = random.randint(0, 15)
                twonl = random.randint(0, 15)
                ncharl = random.randint(0, 50)

                nwonp = random.randint(0, 15)
                nline = random.randint(0, 6)
                tlines = random.randint(0, 6)

                left = random.randint(1, 800)
                top = random.randint(1, 500)
                right = random.randint(1, 500)
                bottom = random.randint(1, 500)

                code = random.choice(possible_codes)
                code2 = random.choice(possible_codes2)

                f.write(
                    'TST {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'
                    .format(
                        stim_id,
                        '',
                        blocknr,
                        subjectnr,
                        pagenr,
                        stim_num,
                        X,
                        Y,
                        fixstart,
                        fixdur,
                        saccindur,
                        saccoutdur,
                        qual,
                        mark,
                        obtnr,
                        0,
                        wlen,
                        nwonl,
                        twonl,
                        ncharl,
                        nwonp,
                        nline,
                        tlines,
                        pagenr_c,
                        left,
                        top,
                        right,
                        bottom,
                        code,
                        code2,
                        0,
                        0,
                        'irrelevant',
                        0,
                        0
                    )
                )

                ffdur = tgdur = rpdur = gdur = weightedRandom(600, 9)
                ffqual = rpqual = tgqual = gqual = weightedRandom(2)

                ffbck = weightedRandom(2)
                ffin = weightedRandom(300)
                ffout = weightedRandom(300)

                rpcnt = weightedRandom(15, 5, 12)
                tgcnt = weightedRandom(15, 5, 12)
                gcnt = weightedRandom(15, 5, 12)

                rpsacc = tgsacc = gsacc = weightedRandom(300)

                rpout = weightedRandom(300)
                tgout = weightedRandom(300)

                gbck = weightedRandom(2)
                gout = weightedRandom(300)

                f2.write(
                    'TST {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'
                    .format(
                        blocknr,
                        subjectnr,
                        stim_id,
                        pagenr_c,
                        code,
                        code2,
                        ffdur,
                        ffqual,
                        ffbck,
                        ffin,
                        ffout,
                        rpdur,
                        rpqual,
                        rpcnt,
                        rpsacc,
                        rpout,
                        tgdur,
                        tgqual,
                        tgcnt,
                        tgsacc,
                        tgout,
                        gdur,
                        gqual,
                        gcnt,
                        gsacc,
                        gbck,
                        gout
                    )
                )
