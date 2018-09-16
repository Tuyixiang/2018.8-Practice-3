"""
STEP 07

Analyze important words in a document
    (standard:
        word length > 1
        weighted occurrence >= 10
        appears in < 5% of all documents
    )

Require: ./seg.json
         ./word_count.json
Produce: ./unique_words.json
         ./unique_word_count.json
"""
if __name__ == '__main__':
    import json

    data = json.load(open('seg.json'))
    word_count = json.load(open('word_count.json'))

    cnt = 0
    for entry in data:
        unique_words = []
        for word in entry['word_count']:
            if len(word) <= 1:
                continue
            # if entry['word_count'][word] < 5:
            #     continue
            le = len(word_count[word])
            if le == 1:
                continue
            # if le > len(data) * 0.1:
            #     continue
            if le < len(data) * 0.05 and entry['word_count'][word] >= 10:
                unique_words.append((word, entry['word_count'][word]))
            # significant_words.append((word, entry['word_count'][word]))
        del entry['word_count']
        # entry['significant_words'] = sorted(significant_words, reverse=True, key=lambda x: x[1])
        entry['unique_words'] = sorted(unique_words, reverse=True, key=lambda x: x[1])

        cnt += 1
        if cnt % 1000 == 0:
            print(cnt)

    result = {}
    for entry in data:
        for (word, occ) in entry['unique_words']:
            if word not in result:
                result[word] = {}
            result[word][entry["id"]] = occ

    result = {key: result[key] for key in result if len(result[key]) > 1}
    for entry in data:
        entry['unique_words'] = [(word, occ) for (word, occ) in entry['unique_words'] if word in result]

    # sort by occurrence
    most_occurred_word = sorted(result, key=lambda key: len(result[key]), reverse=True)

    inverse_index = {word: sorted(result[word], key=lambda x: result[word][x], reverse=True)
                     for word in most_occurred_word}

    json.dump(inverse_index, open("unique_word_count.json", "w"), separators=(',', ':'), ensure_ascii=False)

    json.dump([entry['unique_words'] for entry in data], open('unique_words.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))
