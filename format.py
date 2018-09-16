"""
STEP 03

Pre-process the raw data (all.json)

Require: ./all.json
Produce: ./all.json
"""
if __name__ == "__main__":

    import json
    import re

    data = json.load(open("all.json"))

    qj = '１２３４５６７８９０'
    bj = '1234567890'

    def clear_blank(string):
        return ''.join(filter(lambda x: x not in "\n\r\t 　", string))

    cur = 0
    for i in range(len(data)):
        if cur >= len(data):
            break
        if 'title' not in data[cur] or \
                'content' not in data[cur] or \
                'keywords' not in data[cur] or \
                'publishdate' not in data[cur]:
            data.pop(cur)
            continue

        # format for segmentation
        for j in range(10):
            data[cur]['content'] = re.sub(qj[j], bj[j], data[cur]['content'])
            data[cur]['title'] = re.sub(qj[j], bj[j], data[cur]['title'])
        try:
            (data[cur]['title'], category) = re.sub(r'-+人民网$', '', data[cur]['title']).split('--')[:2]
            data[cur]['category'] = re.sub(r'-.+', '', category)
            data[cur]["id"] = cur
            data[cur]['content'] = re.sub(r'【\d+】', '', data[cur]['content'])
            data[cur]['content'] = re.sub('\n+', '\n', data[cur]['content'])

            data[cur]['description'] = re.sub(r'</?strong>', '', clear_blank(data[cur]['content']))[:100]
            data[cur]['content'] = re.sub('\n', '<br>', data[cur]['content'])
        except Exception as e:
            print(e)
            data.pop(cur)
            continue
        cur += 1

        if cur % 100 == 0:
            print(cur)

    json.dump(data, open('all.json', 'w'), ensure_ascii=False, separators=(',', ':'))
