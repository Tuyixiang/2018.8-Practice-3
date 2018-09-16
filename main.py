"""
STEP 01

Crawler (use with ./crawler.py)

After everything, move these files to ./django_server/data/
all.json
word_count.json
unique_words.json
unique_word_count.json

Produce: ./partials/[num].json
"""
if __name__ == "__main__":
    from crawler import Crawler
    import random
    import json
    import re

    crawler = Crawler()
    crawler.extLinks.add("http://people.com.cn")
    crawler.extend()
    while True:
        if len(crawler.pageLinks) == 0 and len(crawler.extLinks) == 0:
            break
        if len(crawler.pageLinks) and (random.randrange(10) or len(crawler.extLinks) == 0 or len(crawler.extLinks) >= 500):
            try:
                crawler.read_rand()
            except Exception as e:
                print(e)
                if crawler.address in crawler.data:
                    del crawler.data[crawler.address]
                continue
        else:
            try:
                crawler.extend()
                print("ext", crawler.address)
            except Exception as e:
                print(e)
                if crawler.address in crawler.data:
                    del crawler.data[crawler.address]
                continue
        prefix = Crawler.extract_prefix(crawler.address)
        if crawler.address not in crawler.data:
            continue
        elif "content" not in crawler.data[crawler.address] or \
                len(crawler.data[crawler.address]["content"]) < 100:
            if prefix in Crawler.prefix_count:
                Crawler.prefix_count[prefix][0] += 1
                if Crawler.prefix_count[prefix][0] > 10 and \
                        (Crawler.prefix_count[prefix][1] == 0 or
                         Crawler.prefix_count[prefix][0] / Crawler.prefix_count[prefix][1] > 0.5):
                    Crawler.junk_prefix.add(prefix)
                    print("junk:", Crawler.junk_prefix, crawler.address)
                    crawler.pageLinks = set(
                        filter(lambda link: Crawler.extract_prefix(link) not in Crawler.junk_prefix,
                               crawler.pageLinks))
            else:
                Crawler.prefix_count[prefix] = [1, 0]
            del crawler.data[crawler.address]
            continue
        if prefix in Crawler.prefix_count:
            Crawler.prefix_count[prefix][1] += 1
        else:
            Crawler.prefix_count[prefix] = [0, 1]
        l = len(crawler.data)
        print(l, len(crawler.pageLinks), len(crawler.extLinks), len(crawler.extended), crawler.address)
        if l and l % 100 == 0:
            json.dump(crawler.data, open("partials/" + str(l // 100) + ".json", "w"), ensure_ascii=False, sort_keys=True,
                      indent=4)
            for entry in crawler.data:
                if "content" in crawler.data[entry]:
                    crawler.data[entry] = {}
