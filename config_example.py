#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
If you want to download shows from Youtube, you must:
    1. Get a free Youtube API Key ( https://developers.google.com/youtube/v3/getting-started )
    2. Put it in `google_apikey`
    3. Enable the service in `serviceIsEnabled`
'''

google_apikey = "0123456789"

serviceIsEnabled = {
	"onsen": True,
	"youtube": False,
	"bilibili": True,
}

onsen_shows = [
    {
        'enabled': True,
      	'title': 'Shigohaji',
        'showid': "shigohaji",
    },
   	{
        'enabled': True,
        "title": "Kokuradio Road to 2020",
        'showid': "kokuradio",
    }
]

youtube_shows = [
	{
		'enabled': True,
		"title": "Melody Flag",
		"channel": "UCrzFCF_GLRHB0z5ZrYQz4WQ",
		"search": "水瀬いのり MELODY FLAG",
		"idExtractRegex": u'水瀬いのり MELODY FLAG \#(\d+)[^\d]'
	},
]

bilibili_shows = [
	{
		# https://space.bilibili.com/29338618/video?keyword=工作时见不到面所以开始做广播了
		'enabled': True,
		"title": "Shigohaji",
		"channel": 29338618,
		"search": "工作时见不到面所以开始做广播了",
		"idExtractRegex": u'工作时见不到面所以开始做广播了。 第([\d\w]+)回',
		"idSuffix": " premium",
		"urlSuffix": "?p=2",
		"downloadMethod": "annie",
	},
	{
		'enabled': True,
		"title": "Hanazawa Kana no Hitori de dekiru ka na",
		"channel": 29338618,
		"search": "花泽香菜一个人能做到吗",
		"idExtractRegex": u'花泽香菜一个人能做到吗\? 第([\d\w]+)回',
	},
	{
		# https://space.bilibili.com/391100/video?keyword=小原好美のココロおきなく
		'enabled': True,
		"title": "Kohara Konomi's Open Your Heart",
		"channel": 391100,
		"search": "小原好美のココロおきなく",
		"idExtractRegex": u'小原好美のココロおきなく.*\#([\d]+)',
	},
]

# Relative to script path
dlfolder = "out"
