import random
ranks = '23456789TJQKA'
suits = 'CDHS'
def deal_hands():
    deck = [x+y for x in ranks for y in suits]
    random.shuffle(deck)
    return tuple(sorted(deck[n:n+13],key=hand_sort_key) for n in range(0,52,13))
rank_map = {}
hcp_map = {}
for i in range(13):
    rank_map[ranks[i]] = i
    hcp_map[ranks[i]] = max(0,i-8)
suit_map = {'C':0,'D':13,'H':26,'S':39}
hand_sort_key = lambda x: rank_map[x[0]]+suit_map[x[1]]
hand_sort = lambda x: sorted(x,key=hand_sort_key)

def suit_counts(hand):
    counts = {'C':0,'D':0,'H':0,'S':0}
    for card in hand:
        counts[card[1]] += 1
    return counts
def hcp(hand):
    return sum([hcp_map[card[0]] for card in hand])
def lengthpts(hand):
    return sum([max(0,x-4) for x in suit_counts(hand).values()])
def supportpts(hand, trump):
    counts = suit_counts(hand)
    if counts[trump] == 3:
        return sum([max(0,3-x) for x in counts])
    elif counts[trump] >= 4:
        return sum([max(0,5-2*x) for x in counts])
    else:
        return 0
def stopper_counts(hand):
    ''' lower bound, excludes half-stoppers '''
    suits = {'C':'', 'D':'', 'H':'', 'S':''}
    for card in hand_sort(hand):
        suits[card[1]] += card[0]
    stoppers = {}
    for suit in 'CDHS':
        mine = suits[suit][::-1]
        full = ranks[::-1]
        other = ''
        for card in full:
            if card not in mine:
                other += card
        my_ranks = [rank_map[x] for x in mine]
        other_ranks = [rank_map[x] for x in other]
        stoppers[suit] = 0
        opos = 0
        while len(other_ranks) < len(my_ranks):
            other_ranks.append(-1)
        for i in range(len(mine)):
            if my_ranks[i] > other_ranks[opos]:
                stoppers[suit] += 1
            else:
                opos += 1
    return stoppers

def make_bid1(hand, bids, with_description=False):
    ''' uses most of the conventions+system we're using
    (2/1 game forcing, 5 card majors, weak 2-bids, Stayman, etc) '''
    mine = bids[::4]
    lopp = bids[1::4]
    partner = bids[2::4]
    ropp = bids[3::4]
    my_hcp = hcp(hand)
    points = my_hcp + lengthpts(hand)
    counts = suit_counts(hand)
    stoppers = stopper_counts(hand)
    long_major = 'H' if counts['H'] >= counts['S'] else 'S' # defaults to hearts if tie, important for Stayman
    long_minor = 'C' if counts['C'] >= counts['D'] else 'D'
    # opening case
    if bids == ['pass']*len(bids):
        if points >= 22:
            return ('2C', 'strong 2 clubs') if with_description else '2C'
        if counts[long_major] >= 5 and points >= 13: # normal opening
            return ('1'+long_major, 'standard 1-level major opening') if with_description else '1'+long_major
        if counts[long_major] == 6 and 5 <= my_hcp <= 11:
            return ('2'+long_major, 'weak 2-bid, major suit') if with_description else '2'+long_major 
        if counts['D'] == 6 and 5 <= my_hcp <= 11:
            return ('2D', 'weak 2-bid, diamonds') if with_description else '2D' 
        if counts[long_major] < 5: # long_minor must have at least 3 by pigeonhole
            if 13 <= points <= 14:
                return ('1'+long_minor, '1-level minor opening, no major suit') if with_description else '1'+long_minor
            elif 15 <= points <= 17:
                return ('1N', 'standard 1 no-trump opening (15-17 hcp)') if with_description else '1N'
            elif 18 <= points <= 19:
                return ('1'+long_minor, 'no man\'s land minor opening, balanced + 18-19 points') if with_description else '1'+long_minor
            elif 20 <= points <= 21:
                return ('2N', 'standard 2 no-trump opening (20-21 hcp)') if with_description else '1N'
        return ('pass', 'opening pass: <= 12 points, no 6-card suit') if with_description else 'pass'
    # 1-level overcall case: previous opponent opened
    elif bids[:-1] == ['pass']*(len(bids)-1):
        opp_bid = bids[-1]
        if opp_bid[0] == '1' and opp_bid != '1N':
            if suit_map[long_major] > suit_map[opp_bid[1]] and counts[long_major] >= 5 and points >= 9:
                return ('1'+long_major, 'standard 1-level overcall') if with_description else '1'+long_major
            elif opp_bid[1] != 'S' and counts['S'] >= 5 and points >= 9:
                return ('1S', 'standard 1-level overcall') if with_description else '1S'
            elif 15 <= hcp <= 18 and stoppers[opp_bid[1]] >= 1:
                return ('1N', '1 no trump overcall') if with_description else '1N'
            else: # not strong enough to overcall
                return ('pass', '1-level overcall declined-weak hand') if with_description else 'pass'
        else:
            return 'TODO'
    # partner opens, no opponent overcall, no passed hand
    # 2/1 game forcing case
    elif len(bids) >= 2 and (bids == ['pass', bids[-2], 'pass'] or bids == [bids[-2], 'pass']):
        partner_level, partner_suit = bids[-2][0], bids[-2][1]
        if partner_level == 1:
            if points >= 13 and partner_suit in 'DHS':
                if partner_suit == 'S' and counts['H'] >= 5:
                    return ('2H', '2/1 game forcing, >= 13 points + 5H') if with_description else '2H'
                elif partner_suit in 'HS' and counts['D'] > counts['S']:
                    return ('2D', '2/1 game forcing, >= 13 points, diamonds preferred') if with_description else '2D'
                return ('2C', '2/1 game forcing, >= 13 points, 2C response') if with_description else '2C'
            elif 6 <= points <= 12 and partner_suit in 'HS':
                return ('1N', '2/1 game forcing, 6-12 points, 1NT response') if with_description else '1N'
        else:
            return 'TODO'
    # 2/1 game forcing: opener response to forcing 1NT
    elif set(ropp) == {'pass'} and set(lopp) == {'pass'} and mine[0] in ['1H','1S'] and partner == ['1N']:
        orig_suit = mine[0][1]
        other_major = 'H' if orig_suit == 'S' else 'S'
        if counts[orig_suit] >= 6:
            return ('2'+orig_suit, '2/1 forcing response to 1NT, rebid same major suit') if with_description else '2'+orig_suit
        elif counts[other_major] >= 4:
            return ('2'+other_major, '2/1 forcing response to 1NT, bid other major') if with_description else '2'+other_major
        elif 18 <= points <= 19:
            return ('2N', '2/1 forcing response to 1NT, bid 2NT') if with_description else '2N'
        else: 
            return ('2'+long_minor, '2/1 forcing response to 1NT, bid long minor') if with_description else '2'+long_minor
    # Stayman part 1: partner opens/overcalls 1NT or 2NT, right opponent passes
    # promises 8 HCP for 1NT, 5 HCP for 2NT + 4 cards in a major suit
    elif len(partner) > 0 and partner[-1] in ['1N', '2N'] and ropp[-1] == 'pass' \
         and (lopp[-1] != 'pass' or bids[:-2] == ['pass']*(len(bids)-2)) \
         and my_hcp >= (8 if partner[-1] == '1N' else 5) and counts[long_major] >= 4:
        if partner[-1] == '1N':
            return ('2C', 'Stayman stage 1 response to 1NT open/overcall') if with_description else '2C'
        elif partner[-1] == '2N':
            return ('3C', 'Stayman stage 1 response to 1NT open/overcall') if with_description else '3C'
    # Stayman part 2: response to part 1 of Stayman sequence
    elif ((partner[-1] == '2C' and mine[-1] == '1N') or (partner[-1] == '3C' and mine[-1] == '2N')) \
         and ropp[-1] == 'pass' and (ropp[-2] == 'pass' or bids[:-4] == ['pass']*(len(bids)-4)):
        if counts[long_major] >= 4:
            return (partner[-1][0]+long_major, 'Stayman stage 2 response indicating 4-card major') if with_description else partner[-1][0]+long_major
        else:
            return (partner[-1][0]+'D', 'Stayman stage 2 response indicating no 4-card major') if with_description else partner[-1][0]+'D'
    else:
        return 'TODO'
    
