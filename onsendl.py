#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import requests
import urlparse
import hashlib
from pprint import pprint
import config
import subprocess

try:
	# Python 2.6-2.7 
	from HTMLParser import HTMLParser
except ImportError:
	# Python 3
	from html.parser import HTMLParser

ONSEN_APIURL_MOVIEINFO = "http://www.onsen.ag/data/api/getMovieInfo/"

YOUTUBEBASEVIDEOURL = 'https://www.youtube.com/watch?v='
YOUTUBEBASEAPI = 'https://www.googleapis.com/youtube/v3/'

BILIBILI_APIROOT = "https://api.bilibili.com"


def downloadShowEpisode(showConfig, videoInfo, downloadMethod=None):
	if "downloadMethod" in showConfig:
		downloadMethod = showConfig["downloadMethod"]
	elif not downloadMethod:
		downloadMethod = "youtube-dl"
	
	if downloadMethod == "annie":
		return downloadShowEpisodeWithAnnie(showConfig, videoInfo)
	else:
		return downloadShowEpisodeWithYoutubeDl(showConfig, videoInfo)

def downloadShowEpisodeWithAnnie(showConfig, videoInfo):
	outfolder = os.path.join(os.path.dirname(os.path.realpath(
		__file__)), config.dlfolder, showConfig["title"])
	if not os.path.isdir(outfolder):
		os.mkdir(outfolder)

	try:
		epnum = re.search(showConfig["idExtractRegex"], videoInfo["title"].decode(
			"utf-8"), re.UNICODE).group(1)
	except:
		print "WARN: Couldn't extract id from video title:", videoInfo["title"]
		epnum = hashlib.sha1(videoInfo["title"]).hexdigest()

	try: epnum = str(int(epnum))
	except: pass

	if "idSuffix" in showConfig:
		epnum += showConfig["idSuffix"]

	fn = '{} - {}.mp4'.format(showConfig["title"], epnum)
	fnbase = '{} - {}'.format(showConfig["title"], epnum)
	fnmp3 = '{} - {}.mp3'.format(showConfig["title"], epnum)

	fp = os.path.join(outfolder, fn)
	fpbase = os.path.join(outfolder, fnbase)
	fpmp3 = os.path.join(outfolder, fnmp3)
	if os.path.exists(fpmp3):
		print "Already downloaded:", fnmp3
		return False

	url = videoInfo['url']
	if "urlSuffix" in showConfig:
		url += showConfig["urlSuffix"]

	print "Downloading", fnmp3

	print getExistingVideoFilenameFromBaseName(fpbase)
	return False

	if getExistingVideoFilenameFromBaseName(fpbase):
		print "   ", "Video already exists, won't download"
	else:
		print "   ", "Downloading video..."
		cwd = os.getcwd()
		os.chdir(outfolder)
		anniecmd = ["annie", "-O", fnbase, url]
		with open(os.devnull, "w") as devnull:
			subprocess.call(anniecmd, stdout=devnull)
		'''
		subprocess.call(anniecmd)
		'''
		os.chdir(cwd)

	fpvid = getExistingVideoFilenameFromBaseName(fpbase)
	if not fpvid:
		print "   ", "ERROR: Video wasn't downloaded!"
		return False

	print "   ", "Converting to mp3..."
	with open(os.devnull, "w") as devnull:
		subprocess.call(["ffmpeg", "-i", fpvid, fpmp3],
						stdout=devnull, stderr=devnull)
	if not os.path.exists(fpmp3):
		print "   ", "ERROR: Audio wasn't converted! Keeping video."
		return False
	else:
		os.remove(fpvid)

	print "Downloaded"
	return True


def getExistingVideoFilenameFromBaseName(fnbase):
	found = None
	for ext in ("mp4", "flv"):
		fnext = "{}.{}".format(fnbase, ext)
		pprint(fnext)
		if os.path.exists(fnext):
			found = fnext
			break
	return found



def downloadShowEpisodeWithYoutubeDl(showConfig, videoInfo):
	outfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), config.dlfolder,showConfig["title"])
	if not os.path.isdir(outfolder):
		os.mkdir(outfolder)

	try:
		epnum = re.search(showConfig["idExtractRegex"], videoInfo["title"].decode("utf-8"), re.UNICODE).group(1)
	except:
		print "WARN: Couldn't extract id from video title:", videoInfo["title"]
		epnum = hashlib.sha1(videoInfo["title"]).hexdigest()

	try: epnum = str(int(epnum))
	except: pass

	if "idSuffix" in showConfig:
		epnum += showConfig["idSuffix"]

	fn = '{} - {}.mp4'.format(showConfig["title"], epnum)
	fnmp3 = '{} - {}.mp3'.format(showConfig["title"], epnum)

	fp = os.path.join(outfolder, fn)
	fpmp3 = os.path.join(outfolder, fnmp3)
	if os.path.exists(fpmp3):
		print "Already downloaded:", fnmp3
		return False

	url = videoInfo['url']
	if "urlSuffix" in showConfig:
		url += showConfig["urlSuffix"]

	print "Downloading", fnmp3

	cmd = [
		"youtube-dl",
		"-o", fp, 
		"--extract-audio", "--audio-format", "mp3", "--audio-quality", "128K",
		videoInfo['url'],
	]
	subprocess.call(cmd)

	print "Downloaded"
	return True


def bilibiliGetVideoList(spaceid, searchstr):
	try:
		url = "%s/x/space/arc/search?mid=%s&ps=5&tid=0&pn=1&keyword=%s&order=pubdate&jsonp=jsonp" % (
			BILIBILI_APIROOT, spaceid, searchstr)
		x = requests.get(url)
		x = x.json()

		videos = []
		for videoraw in x['data']['list']['vlist']:
			videos.append({
				'aid': videoraw['aid'],
				'title': videoraw['title'].encode("utf-8"),
				'url': 'https://www.bilibili.com/video/av%s' % videoraw['aid']
			})

		return videos
	except:
		return []


def downloadBilibiliShowEpisode(showConfig, videoInfo):
	return downloadShowEpisode(showConfig, videoInfo)

def youtubeGetLatestVideosFromChannel(channel_id, titleMatcher=None):
	try:
		url = YOUTUBEBASEAPI+'search?key={}&channelId={}&type=video&part=snippet,id&order=date&maxResults=10'.format(config.google_apikey, channel_id)
		r = requests.get(url)
		data = r.json()

		h = HTMLParser()
		
		videos = []
		for x in data["items"]:
			try:
				videos.append({
					"id": x["id"]["videoId"],
					"title": h.unescape(x["snippet"]["title"]).encode("utf-8"),
					"publishedAt": x["snippet"]["publishedAt"],
					"url": YOUTUBEBASEVIDEOURL+str(x["id"]["videoId"])
				})
			except:
				pass

		if titleMatcher:
			videos = [x for x in videos if titleMatcher in x["title"]]
		
		return videos
	except Exception as e:
		raise
		return []


def downloadYoutubeShowEpisode(showConfig, videoInfo):
	return downloadShowEpisode(showConfig, videoInfo)

def onsenGetProgramInfoFromId(id, auth):
	x = requests.get("https://app.onsen.ag/api/me/downloads/"+str(id), allow_redirects=True, headers={
		'X-Device-Identifier': '3785A781-F9EF-4339-8AF8-05ED15AD07BA',
		'X-App-Version': '25',
		'Accept-Language': 'en;q=1.0, es-ES;q=0.9, ja;q=0.8',
		'Accept-Version': 'v3',
		'Content-Type': 'application/json',
		'Accept': '*/*',
		'User-Agent': 'iOS/Onsen/2.6.1',
		'Content-Length': '0',
		'Authorization': 'Bearer '+auth,
		'X-Device-Os': 'ios',
		'Host': 'app.onsen.ag',
		'X-Device-Name': 'GLaDOS'
	})
	return x.json()


def onsenGetProgramInfo(show):
	'''
	Returns dict containing, among others:
		* update (date in format 2019.12.2)
		* count (episode number)
		* file (url of the file)
	'''
	try:
		showname = show["showid"]

		x = requests.get(ONSEN_APIURL_MOVIEINFO+showname, allow_redirects=True)
		x = re.search(r"^callback\((\{.*\})\);$", x.text)
		x = json.loads(x.group(1))

		x["file"] = x["moviePath"]["iPhone"]

		x["title"] = show["title"] if "title" in show else showname.capitalize()

		return x
	except:
		print "An error ocurred downloading show info from", showname
		return None
	
def downloadFromProgramInfo(info):
	if not info:
		return False

	ext = os.path.splitext(urlparse.urlparse(info["file"]).path)[1]
	fn = info["title"] + " - " + info["count"] + " ["+ info["update"] +"]"+ext
	
	fdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), config.dlfolder, info["title"])
	try: os.mkdir(fdir)
	except: pass

	fp = os.path.join(fdir, fn)

	if os.path.exists(fp):
		print "Already downloaded", fn
		return False

	print "Downloading", fn
	r = requests.get(info["file"], allow_redirects=True)
	with open(fp, 'wb') as f:
		f.write(r.content)

	print "Downloaded"

	return True



def main():
	if config.serviceIsEnabled["onsen"]:
		for show in config.onsen_shows:
			if not show['enabled']: continue
			info = onsenGetProgramInfo(show)
			downloadFromProgramInfo(info)
	
	if config.serviceIsEnabled["youtube"]:
		for show in config.youtube_shows:
			if not show['enabled']: continue
			videos = youtubeGetLatestVideosFromChannel(show["channel"], show["search"])
			for video in videos:
				downloadYoutubeShowEpisode(show, video)
	
	if config.serviceIsEnabled["bilibili"]:
		for show in config.bilibili_shows:
			if not show['enabled']: continue
			videos = bilibiliGetVideoList(show["channel"], show["search"])
			for video in videos:
				downloadBilibiliShowEpisode(show, video)
	



if __name__ == "__main__":
	main()
