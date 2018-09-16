"""
STEP 04

This module applies segmentation on pages,
    separately on title, content and keywords
        weight: 10x for title, 4x for keywords, 1x for content

Require: ./all.json
Produce: ./seg_partials/seg[num].json
"""

if __name__ == "__main__":

    import json
    import jieba
    import copy

    jieba.initialize()

    data = json.load(open("all.json"))

    redundant = "“”’‘，。、；：！？…@#$￥%&*（）《》【】-—+=`~,./<>?;:\'\"[]{}/\\|()\n\r\t 　" \
                "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


    def clear_character(string, char_set):
        return ''.join(filter(lambda x: x not in char_set, string))


    output = []
    for cur in range(len(data)):
        output.append(copy.deepcopy(data[cur]))

        title = clear_character(data[cur]['title'], redundant)
        content = clear_character(data[cur]["content"], redundant)
        keywords = clear_character(data[cur]["keywords"], redundant)

        # segmentation
        contentSeg = jieba.lcut_for_search(content)
        titleSeg = jieba.lcut_for_search(title)
        keywordSeg = jieba.lcut_for_search(keywords)

        # count word
        word_count = {}
        for word in contentSeg:
            if word not in word_count:
                word_count[word] = contentSeg.count(word)

        title_count = {}
        for word in titleSeg:
            if word not in title_count:
                title_count[word] = titleSeg.count(word) * 10
        for word in title_count:
            if word not in word_count:
                word_count[word] = title_count[word]
            else:
                word_count[word] += title_count[word]

        keyword_count = {}
        for word in keywordSeg:
            if word not in keyword_count:
                keyword_count[word] = keywordSeg.count(word) * 4
        for word in keyword_count:
            if word not in word_count:
                word_count[word] = keyword_count[word]
            else:
                word_count[word] += keyword_count[word]

        output[-1]["word_count"] = word_count
        output[-1]['title'] = title
        del output[-1]['keywords']
        del output[-1]['content']
        del output[-1]['publishdate']
        del output[-1]['title']
        del output[-1]['source']
        del output[-1]['category']
        del output[-1]['description']

        if cur % 1000 == 0:
            print(cur)
            json.dump(output, open('seg_partials/seg' + str(cur // 1000) + '.json', 'w'),
                      ensure_ascii=False, separators=(',', ':'))
            output = []
