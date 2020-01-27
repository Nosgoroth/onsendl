# Onsendl radio downloader

A somewhat hacky script that downloads radio shows from a number of online services:

* Onsen (音泉, [onsen.ag](http://www.onsen.ag)) - free shows, premium not supported
* Youtube
* Bilibili

I wanted to download shows from Hibiki, but it doesn't seem to offer on-demand listening, so downloading rips from Bilibilin seemed like an acceptable alternative.

This script is for my use and I can't guarantee that it will work on any other environment. I won't actively solve issues, but if you want to submit a pull request I'll be happy to have that as long as it doesn't break my usage. You're welcome to fork.

## Dependencies

* Python 2.x. Sorry about that.
* The `requests` library.
* For Youtube and Bilibili shows, the `youtube-dl` CLI video downloader and `ffmpeg`
* Optionally, the `annie` CLI video downloader.

This has only been tested on a Mac, so no promises about other operating systems.

## Getting started

* Clone the repo
* Copy `config_example.py` as `config.py`
* Edit `config.py`. It already has some example shows. They work at the moment of writing.
* If you want to use Youtube as a source service, get an API key, put it in `config.py` and enable the service.

## Configuring a show

The `enabled` key is required in all configs.

### Onsen

Onsen show definitions have the following structure and available configuration keys:

```py
{
    'enabled': True,
    "title": "Kokuradio Road to 2020",
    'showid': "kokuradio",
}
```

The `title` key is optional. If not provided, the showid wil be used (capitalised).

You can get the showid from the show page url. For example Shigohaji's show page url is `http://www.onsen.ag/program/shigohaji/`.

Onsen shows are downloaded directly as mp3, so there's no need for external tools like `youtube-dl` or `ffmpeg`.

### Youtube and Bilibili

Youtube and Bilibili show definitions have the following structure and available configuration keys:

```py
{
    'enabled': True,
    "title": "Shigohaji",
    "channel": 29338618,
    "search": "工作时见不到面所以开始做广播了",
    "idExtractRegex": u'工作时见不到面所以开始做广播了。 第([\d\w]+)回',
    "idSuffix": " premium",
    "urlSuffix": "?p=2",
    "downloadMethod": "annie",
}
```

The `title` and `channel` keys are required. The `search` key is optional in Youtube but required in Bilibili. The rest of the parameters are optional.

If a `downloadMethod` with a value of `annie` isn't specified, `youtube-dl` will be used.

For `idExtractRegex` the first capturing group of the regular expression will be used as the episode number. If the regex doesn't match, a sha1 of the video title will be used.

#### Channel id

You can get the channel id from its URL:

* Bilibili: `29338618` from `https://space.bilibili.com/29338618/video?keyword=工作时见不到面所以开始做广播了`
* Youtube: `UCYBwKaLwCGY7k3auR_FLanA` from `https://www.youtube.com/channel/UCYBwKaLwCGY7k3auR_FLanA`

## What do I do now

Just run the script: `python onsendl.py`. The check for previously downloaded episodes is very basic: if the episode isn't there, it gets downloaded. Shows are downloaded into subfolders of the configured relative download path.

After download, I suggest you leave the shows there and copy the files if you need them somewhere else.

Some more ideas and suggestions:

* Automate regular runs of this script via `crontab` or similar so that you'll always have the latest shows.
* Build a webapp that read the files in the output folder of this script and generates RSS feeds that you can feed your podcast app of choice.
