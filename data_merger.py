"""
STEP 02

Merge all the data

Require: ./partials/[num].json
Produce: ./all.json
"""
if __name__ == "__main__":
    import json
    maxIndex = 100
    dataList = []
    for i in range(2, maxIndex + 1):
        part = json.load(open("partials/" + str(i) + ".json"))
        for key in part:
            if "content" in part[key]:
                part[key]['source'] = key
                dataList.append(part[key])
    json.dump(dataList, open("all.json", "w"), separators=(',', ':'), ensure_ascii=False)
