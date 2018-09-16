"""
STEP 06

Read all word segmentations and construct a reverse search dict

Require: ./seg.json
Produce: ./word_count.json
"""
if __name__ == "__main__":
    import json

    result = {}
    data = json.load(open("seg.json"))

    cnt = 0
    for entry in data:
        for word in entry['word_count']:
            if word not in result:
                result[word] = {}
            result[word][entry["id"]] = entry['word_count'][word]
        cnt += 1
        print(cnt / len(data), "\r")

    # sort by occurrence
    most_occurred_word = sorted(result, key=lambda key: len(result[key]), reverse=True)

    inverse_index = {word: sorted(result[word], key=lambda x: result[word][x], reverse=True)
                     for word in most_occurred_word}
    json.dump(inverse_index, open("word_count.json", "w"), separators=(',', ':'), ensure_ascii=False)
