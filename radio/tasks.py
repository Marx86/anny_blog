import requests
from BeautifulSoup import BeautifulSoup
import os
import sys
import vkontakte
from os import system
from datetime import datetime

add_path = '/'.join(os.path.split(os.path.abspath(__file__))[0].split('/')[:-1])
sys.path.append(add_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anny_blog.settings")

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()
from django.conf import settings
from django.core.files import File
from radio.models import Audio


def vk_login():
    url = 'https://oauth.vk.com/authorize'
    query = {
        'client_id': settings.VK_STANDALONE_APP_ID,
        'scope': 'audio,groups,stats',
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'v': '5.2',
        'response_type': 'token',
    }
    r = requests.get(url, params=query)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        form = soup.find('form')
        action = dict(form.attrs)['action']
        inputs = form.findAll('input')

        post_data = {}
        for input in inputs:
            attrs = dict(input.attrs)
            if attrs['name'] != 'submit':
                post_data[attrs['name']] = attrs.get('value')

        post_data['email'] = settings.VK_EMAIL
        post_data['pass'] = settings.VK_PASS

        r = requests.post(action, data=post_data)
        query = r.url.split('#')[1]
        args = dict(item.split('=') for item in query.split('&'))

        return args['access_token']

def add_song(song):
    mp3_file = os.path.join(Audio.file_dir(), 'tmp', '%i.mp3' % song['aid'])

    fd_mp3 = open(mp3_file, 'w+')
    result = requests.get(song['url'])
    fd_mp3.write(result.content)
    fd_mp3.close()

    ogg_file = os.path.join(Audio.file_dir(), 'tmp',
                            '%s.ogg' % song['aid'].__str__())
    system('ffmpeg -y -i %s -acodec libvorbis -ar 44100 -aq 2.3 %s' \
                                                % (mp3_file, ogg_file))

    fd_ogg = open(ogg_file)
    fd_mp3 = open(mp3_file)
    song.pop('owner_id', None)
    song.pop('url', None)

    audio = Audio(**song)
    audio.ogg.save('%i.ogg' % song['aid'], File(fd_ogg))
    audio.mp3.save('%i.mp3' % song['aid'], File(fd_mp3))
    audio.save()

    fd_ogg.close()
    fd_mp3.close()

    os.remove(mp3_file)
    os.remove(ogg_file)

def get_audio():
    token = vk_login()
    vk = vkontakte.API(token=token)
    vk_audio = vk.audio.get(gid=settings.VK_GROUP_ID)
    vk_aids = [a['aid'] for a in vk_audio]
    db_audio = Audio.objects.all()
    db_aids = [a.aid for a in db_audio]

    for audio in vk_audio:
        if audio['aid'] not in db_aids:
            print '[%s] INFO: Create audio instance %s-%s ...' % (datetime.utcnow(),
                                                                audio['artist'],
                                                                audio['title'])
            add_song(audio)

    # Delete removed vk songs
    [a.delete() for a in db_audio if a.aid not in vk_aids]


if __name__ == '__main__':
    get_audio()
