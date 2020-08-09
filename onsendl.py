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

ONSEN_APIURL_MOVIEINFO = "https://www.onsen.ag/web_api/programs/"

YOUTUBEBASEVIDEOURL = 'https://www.youtube.com/watch?v='
YOUTUBEBASEAPI = 'https://www.googleapis.com/youtube/v3/'

BILIBILI_APIROOT = "https://api.bilibili.com"


def downloadHlsStreamWithFFmpeg(url, filename):
	'''
	ffmpeg -i
	-bsf:a aac_adtstoasc -vn -crf 50 file.mp3
	'''
	ffmpegcmd = ['ffmpeg', '-i', url, filename]
	with open(os.devnull, "w") as devnull:
		subprocess.call(ffmpegcmd, stdout=devnull)


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
	if os.path.exists(fpmp3) or (
		'video' in showConfig and showConfig['video']
		and getExistingVideoFilenameFromBaseName(fpbase)
		):
		print "Already downloaded:", fnbase
		return False

	url = videoInfo['url']
	if "urlSuffix" in showConfig:
		url += showConfig["urlSuffix"]

	print "Downloading", fnbase

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

	if 'video' in showConfig and showConfig['video']:
		print "Downloaded as video"
		return True

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

	basename = '{} - {}'.format(showConfig["title"], epnum)
	fn = '{} - {}.mp4'.format(showConfig["title"], epnum)
	fnmp3 = '{} - {}.mp3'.format(showConfig["title"], epnum)

	fp = os.path.join(outfolder, fn)
	fpmp3 = os.path.join(outfolder, fnmp3)
	if os.path.exists(fpmp3) or (
		'video' in showConfig and showConfig['video']
		and os.path.exists(fp)
		):
		print "Already downloaded:", fnmp3
		return False

	url = videoInfo['url']
	if "urlSuffix" in showConfig:
		url += showConfig["urlSuffix"]

	print "Downloading", basename

	cmd = None
	expectedFile = None
	if 'video' in showConfig and showConfig['video']:
		cmd = [
			"youtube-dl",
			"-o", fp,
			videoInfo['url'],
		]
		expectedFile = fp
	else:
		cmd = [
			"youtube-dl",
			"-o", fp, 
			"--extract-audio", "--audio-format", "mp3", "--audio-quality", "128K",
			videoInfo['url'],
		]
		expectedFile = fpmp3
	
	subprocess.call(cmd)

	if os.path.exists(expectedFile):
		print "Downloaded"
		return True
	else:
		print "Couldn't download"
		return False


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

def youtubeGetLatestVideosFromChannel(channel_id, titleMatcher=None, maxResults=10):
	try:
		url = YOUTUBEBASEAPI+'search?key={}&channelId={}&type=video&part=snippet,id&order=date&maxResults={}'.format(config.google_apikey, channel_id, maxResults)
		r = requests.get(url)
		data = r.json()

		if not data:
			raise Exception("No data received")
		if "error" in data and "message" in data["error"]:
			raise Exception(data["error"]["message"])
		if "error" in data and "code" in data["error"] and data["error"]["code"] >= 400:
			raise Exception(data["error"]["code"])

		#pprint(data)

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
		print "Youtube:", e
		return []


def downloadYoutubeShowEpisode(showConfig, videoInfo):
	return downloadShowEpisode(showConfig, videoInfo)


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
		# x = re.search(r"^callback\((\{.*\})\);$", x.text)
		x = x.json()

		title = x["current_episode"]["title"]
		episodes = [item for item in x["contents"] if item["latest"]]
		if not len(episodes):
			print "No episodes available for", showname
			return None
		episode = episodes[0]
		x["episode"] = episode
		x["m3u8"] = episode["streaming_url"]

		x["title"] = show["title"] if "title" in show else showname.capitalize()

		eptitle = episode["title"]

		if "idExtractRegex" in show:
			try:
				eptitle = re.search(show["idExtractRegex"], eptitle, re.UNICODE).group(1)
			except:
				print "WARN: Couldn't extract id from video title:", eptitle

		try:
			eptitle = str(int(eptitle))
		except:
			pass

		x["eptitle"] = eptitle

		return x
	except Exception as ex:
		print "An error ocurred downloading show info from", showname
		return None
	
def downloadFromProgramInfo(info):
	if not info:
		return False

	eptitle = info["eptitle"]
	date = info["current_episode"]["delivery_date"]

	fn = "%s - %s.mp3" % (info["title"], eptitle)
	
	fdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), config.dlfolder, info["title"])
	try: os.mkdir(fdir)
	except: pass

	fp = os.path.join(fdir, fn)

	if os.path.exists(fp):
		print "Already downloaded", fn
		return False

	print "Downloading", fn

	downloadHlsStreamWithFFmpeg(info["m3u8"], fp)
	
	#r = requests.get(info["file"], allow_redirects=True)
	#with open(fp, 'wb') as f:
	#	f.write(r.content)

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
			maxResults = show["maxResults"] if "maxResults" in show else 10
			videos = youtubeGetLatestVideosFromChannel(show["channel"], show["search"], maxResults)
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
