from django.shortcuts import render_to_response, redirect
import json
import time
import jieba
from random import randrange

jieba.initialize()

now = time.time_ns()
data = json.load(open("data/all.json"))
print("all.json loaded in", (time.time_ns() - now) / 1000000000, "s")
now = time.time_ns()
word_data = json.load(open("data/word_count.json"))
print("word_count.json loaded in", (time.time_ns() - now) / 1000000000, "s")
now = time.time_ns()
unique_words = json.load(open('data/unique_words.json'))
print("unique_words.json loaded in", (time.time_ns() - now) / 1000000000, "s")
now = time.time_ns()
unique_word_data = json.load(open('data/unique_word_count.json'))
print("unique_word_count.json loaded in", (time.time_ns() - now) / 1000000000, "s")


def index(request):
    return render_to_response('list.html')
    # return HttpResponse("123")


def browse(request, page):
    response_object = {
        "data": data[(page - 1) * 10:page * 10],
        "page": page,
        "total_page": (len(data) + 9) // 10,
        "total": len(data),
    }
    return render_to_response('list.html', response_object)


def search_home(request):
    response_object = {
        "total": len(data),
    }
    return render_to_response('search.html', response_object)


def advanced_search_home(request):
    response_object = {
        "total": len(data),
    }
    return render_to_response('advanced_search.html', response_object)


def search_result(request, text, page):
    start_time = time.time_ns()

    text_list = jieba.lcut(text, cut_all=False)
    text_list = [word for word in text_list if word in word_data and word != ' ']

    if len(text_list) > 1:
        result_list = {}
        for word in text_list:
            for i in range(len(word_data[word])):
                if word_data[word][i] in result_list:
                    result_list[word_data[word][i]] += 2 - i / len(word_data[word])
                else:
                    result_list[word_data[word][i]] = 2 - i / len(word_data[word])
        result_list = {x: result_list[x] for x in result_list if result_list[x] >= len(text_list)}
        result_list = sorted(result_list, key=lambda x: result_list[x], reverse=True)

        response_object = {
            "data": [data[entry_id] for entry_id in result_list][(page - 1) * 10:page * 10],
            "page": page,
            "results": (len(result_list)),
            "total_page": (len(result_list) + 9) // 10,
            "search_text": text,
            "keywords": text_list,
            "time": time.time_ns() - start_time
        }
    elif len(text_list) == 1:
        result_list = word_data[text]
        response_object = {
            "data": [data[entry_id] for entry_id in result_list][(page - 1) * 10:page * 10],
            "page": page,
            "results": (len(result_list)),
            "total_page": (len(result_list) + 9) // 10,
            "search_text": text,
            "keywords": text_list,
            "time": time.time_ns() - start_time
        }
    else:
        response_object = {
            "data": [],
            "page": 0,
            "results": 0,
            "total_page": 0,
            "search_text": text,
            "keywords": text_list,
            "time": time.time_ns() - start_time
        }
    return render_to_response('search_result.html', response_object)


def advanced_search_result(request, text, start_date, end_date, page):
    start_time = time.time_ns()

    text_list = jieba.lcut(text, cut_all=False)
    text_list = [word for word in text_list if word in word_data and word != ' ']

    if text_list:
        result_list = {}
        for word in text_list:
            for i in range(len(word_data[word])):
                date = data[word_data[word][i]]['publishdate']
                if date < start_date or date > end_date:
                    continue
                if word_data[word][i] in result_list:
                    result_list[word_data[word][i]] += 2 - i / len(word_data[word])
                else:
                    result_list[word_data[word][i]] = 2 - i / len(word_data[word])
        result_list = {x: result_list[x] for x in result_list if result_list[x] >= len(text_list)}
        result_list = sorted(result_list, key=lambda x: result_list[x], reverse=True)
        if result_list:
            response_object = {
                "data": [data[entry_id] for entry_id in result_list][(page - 1) * 10:page * 10],
                "page": page,
                "results": (len(result_list)),
                "total_page": (len(result_list) + 9) // 10,
                "search_text": text,
                "keywords": text_list,
                "time": time.time_ns() - start_time,
                "startdate": start_date,
                "enddate": end_date,
            }
            return render_to_response('advanced_search_result.html', response_object)
    response_object = {
        "data": [],
        "page": 0,
        "results": 0,
        "total_page": 0,
        "search_text": text,
        "keywords": text_list,
        "time": time.time_ns() - start_time,
        "startdate": start_date,
        "enddate": end_date,
    }
    return render_to_response('advanced_search_result.html', response_object)


def view_page(request, page_id):
    words = unique_words[page_id]
    recommendation = []
    if words:
        recommendation = {}
        for (word, occ) in words:
            for entry in unique_word_data[word]:
                if entry in recommendation:
                    recommendation[entry] += 1
                else:
                    recommendation[entry] = 1
        recommendation = sorted(recommendation, key=lambda x: recommendation[x], reverse=True)[:4]
    response_object = {
        **data[page_id],
        "recommend": [data[ind] for ind in recommendation if ind != page_id][:3],
    }
    return render_to_response('page_view.html', response_object)


def random(request):
    return redirect(view_page, page_id=randrange(len(data)))
