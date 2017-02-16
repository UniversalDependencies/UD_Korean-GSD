import re
import sys

PUNCT_TAGS = set(['SF', 'SP', 'SS', 'SE', 'SO', 'SW'])

def get_tree(fin):
    sent = fin.readline()
    if not sent: return (None, None, None)
    text = fin.readline()
    koma = fin.readline()
    tree = []

    for line in fin:
        l = line.split()
        if l:
            l[0] = int(l[0])
            l[6] = int(l[6])
            tree.append(l)
        else: break

    return (sent, text, tree)

def split_morphems(m):
    m = m.replace('++', '+-PLUS-')
    m = m.replace('//', '-FWS-/')
    return [t.split('/') for t in m.split('+')]

def join_morphemes(morphemes):
    return '+'.join(['/'.join(t) for t in morphemes])

def reorder(tree, idx):
    for i,node in enumerate(tree,1):
        node[0] = i
        if node[6] > idx: node[6] += 1

def tokenize_final_symbol(tree, node, morphemes):
    p = morphemes[-1][0]
    if not node[1].endswith(p): return

    pnode    = node[:]
    node[1]  = node[1][:node[1].rfind(p)]
    node[9]  = 'SpaceAfter=No'
    node[10] = join_morphemes(morphemes[:-1])

    pnode[1]  = p
    pnode[3]  = 'PUNCT'
    pnode[4]  = '.'
    pnode[6]  = node[0]
    pnode[7]  = 'punct'
    pnode[10] = '/'.join(morphemes[-1])

    idx = tree.index(node) + 1
    tree.insert(idx, pnode)
    reorder(tree, idx)

def tokenize_front_symbol(tree, node, morphemes):
    p = morphemes[0][0]
    if not node[1].startswith(p): return

    pnode    = node[:]
    node[1]  = node[1][len(p):]
    node[10] = join_morphemes(morphemes[1:])

    pnode[1]  = p
    pnode[3]  = 'PUNCT'
    pnode[4]  = '.'
    pnode[6]  = node[0]
    pnode[7]  = 'punct'
    pnode[9]  = 'SpaceAfter=No'
    pnode[10] = '/'.join(morphemes[0])

    idx = tree.index(node)
    tree.insert(idx, pnode)
    reorder(tree, idx)

def tokenize_middle_symbol(tree, node, morphemes, idx):
    p = morphemes[idx][0]
    i = node[1].index(p)
    if i < 0: return
    word = node[1]

    nnode = node[:]
    nnode[1]  = word[i+len(p):]
    nnode[9]  = 'validate'
    nnode[10] = join_morphemes(morphemes[idx+1:])

    node[1]  = word[:i+len(p)]
    node[6]  = node[0]
    node[7]  = 'compound'
    node[9]  = 'validate'
    node[10] = join_morphemes(morphemes[:idx+1])

    idx = tree.index(node)
    tree.insert(idx+1, nnode)
    reorder(tree, idx)

    #tokenize_final_symbol(tree, node, morphemes[:idx+1])







    

def process(tree):
    for i, node in enumerate(tree):
        # make the previous node as the head of punctuation
        if i > 0 and node[3] == 'PUNCT' and tree[i-1][9] == 'SpaceAfter=No': node[6] = i
        morphemes = split_morphems(node[-1])
        if len(morphemes) <= 1: continue      # skip if there is only one morpheme

        if morphemes[-1][1] in PUNCT_TAGS:
            tokenize_final_symbol(tree, node, morphemes)
        elif morphemes[0][1] in PUNCT_TAGS:
            tokenize_front_symbol(tree, node, morphemes)
        else:
            node[-1] = join_morphemes(morphemes)
            # idx = next((i for i,t in enumerate(morphemes) if t[1] == 'SS'), -1)
            # if 0 < idx < len(morphemes)-1: tokenize_middle_symbol(tree, node, morphemes, idx)
            # else: node[-1] = join_morphemes(morphemes)

    for node in tree:
        node[0] = str(node[0])
        node[6] = str(node[6])


IN_FILE  = sys.argv[1]
OUT_FILE = sys.argv[1]+'.tok'
fin  = open(IN_FILE)
fout = open(OUT_FILE, 'w')

while 1:
    (sent, text, tree) = get_tree(fin)
    if not tree: break
    process(tree)
    fout.write(sent)
    fout.write(text)
    fout.write('\n'.join(['\t'.join(node) for node in tree])+'\n\n')
    