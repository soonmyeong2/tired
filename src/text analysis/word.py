def tag_counting(file):


    f = open(file, "r")
    lines = f.read()

    from konlpy.tag import Twitter

    nlpy = Twitter()
    nouns = nlpy.nouns(lines)

    from collections import Counter

    count = Counter(nouns)

    tag_count = []
    tags = []

    for n, c in count.most_common(100):
        dics = {'tag': n, 'count': c}
        if len(dics['tag']) >= 2 and len(tags) <= 49:
            tag_count.append(dics)
        tags.append(dics['tag'])

    for tag in tag_count:
        print(" {:<14}".format(tag['tag']), end='\t')
    print("{}".format(tag['count']))

    print("\n---------------------------------")
    print("     명사 총  {}개".format(len(tags)))
    print("---------------------------------\n\n")

    return tags

    tags = tag_counting(file="blog.txt")
    print(tags)
