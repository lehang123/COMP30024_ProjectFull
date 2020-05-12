from math import tanh
from teamProject.utils import get_clusters, boom_zone, lists_to_tuples, boom_affected_num, speedy_manhattan


def mobility_eval(board, next_turn, is_soft=False):
    """
    a simple eval method that return the value for a current board

    evaluate by mobility

    :param board: the board after move
    :param next_turn: the color that's going to move in this board configuration(the move after board)
    :param is_soft: is it a soft eval so that I can speed things up
    :return: the value of the board
    """

    white_stacks = board['white']
    black_stacks = board['black']

    white_pieces_num = sum([n for n, x, y in white_stacks])
    black_pieces_num = sum([n for n, x, y in black_stacks])

    if not white_stacks and black_stacks:
        return -1
    if not black_stacks and white_stacks:
        return 1
    if not black_stacks and not black_stacks:
        return 0

    white_clusters = get_clusters(white_stacks.copy())
    black_clusters = get_clusters(black_stacks.copy())

    white_clusters_bzs = []
    black_clusters_bzs = []

    white_control_score = control_score_fast(white_clusters, white_clusters_bzs, is_soft=is_soft)
    black_control_score = control_score_fast(black_clusters, black_clusters_bzs, is_soft=is_soft)

    white_choke_points = []
    black_choke_points = []

    get_choke_points(white_choke_points, white_clusters_bzs)
    get_choke_points(black_choke_points, black_clusters_bzs)

    white_choke_points_score = choke_points_score(white_choke_points, white_stacks, black_stacks, black_pieces_num)
    black_choke_points_score = choke_points_score(black_choke_points, black_stacks, white_stacks, white_pieces_num)

    # w1=5, w2=1, w3=2
    final_score = 5 * ((white_pieces_num - black_pieces_num) / float(12)) \
                  + (white_control_score - black_control_score) + 2 * (
                          white_choke_points_score - black_choke_points_score)

    return tanh(final_score)


def get_choke_points(choke_points, clusters_bzs):
    """
    get the fatal positions
    :param choke_points: fatal positions that if boom happens one party will lose all tokens
    :param clusters_bzs: boom zones of clusters
    """
    dic = {}
    for cluster_bzs in clusters_bzs:
        for bz in cluster_bzs:
            dic[bz] = dic.get(bz, 0) + 1

    max_occur = 0
    max_occur_position = ()

    for key in dic:
        occur = dic[key]
        if occur > max_occur:
            max_occur = occur
            max_occur_position = key

    choke_points.append(max_occur_position)

    clusters_bzs = [cluster_bzs for cluster_bzs in clusters_bzs if max_occur_position not in cluster_bzs]

    if clusters_bzs:
        get_choke_points(choke_points, clusters_bzs)


def choke_points_score(choke_points, stacks, blocks, blocks_num):
    """
    calsulate the fatal point score
    :param choke_points: fatal points
    :param stacks: stacks around the fatal point
    :param blocks: separate clusters (not linked together)
    :param blocks_num: number of separate clusters (not linked together)
    :return: the fatal point score
    """
    score = 0
    if blocks_num < len(choke_points):
        return 1.0
    for cp in choke_points:
        affected_num = boom_affected_num(cp, stacks.copy())

        shortest = min([speedy_manhattan(cp, b) for b in blocks])

        score += (12 - affected_num + 3 * shortest)

    # 372 is the highest score possible in perfect situation
    return score / float(372.0)


def control_score_fast(clusters, cluster_bzs, is_soft=False):
    """
    calculate the control score
    :param clusters: clusters
    :param cluster_bzs: clusters' boom zones
    :param is_soft: whether implement the function as soft evaluation
    :return: the control score
    """
    p_dict = {}
    stack_ps = []
    for cluster in clusters:
        cbz = set()
        total = 0
        for n, x, y in cluster:
            total += n
            stack_ps.append((x, y))
            boom_zones = lists_to_tuples(boom_zone([x, y], exclude_self=False, check_valid=True))
            cbz = cbz.union(boom_zones)

        cbz = [b for b in cbz if b not in stack_ps]
        cluster_bzs.append(cbz)
        for c in cbz:
            p_dict[c] = p_dict.get(c, 12) - total

    score = 0
    for key in p_dict:
        score += p_dict[key]

    # 704 is the highest score possible in perfect situation
    return score / float(704.0)
