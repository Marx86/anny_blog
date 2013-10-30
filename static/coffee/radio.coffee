play_pause = () ->
  radio = document.getElementById 'radio'
  if radio.paused
    find_track radio
    radio.play()
    set_cookie 'radio_pause', 0
    $('#radio-img').attr 'src', '/static/img/radio_play.png'
  else
    radio.pause()
    set_cookie 'radio_pause', 1
    set_cookie 'radio_current_time', radio.currentTime
    $('#radio-img').attr 'src', '/static/img/radio.png'
  false

find_track = (radio) ->
  if radio.src
    if radio.currentTime
      return null
    else
      [current_time, id] = get_from_cookies()
      if current_time
        radio.currentTime = current_time
      return null
  else
    [current_time, id] = get_from_cookies()
    if id
      _id = id * 1
      for track in PLAYLIST
        if track.id == _id
          set_track track, radio
          console.log 1
          console.log radio
          if current_time and radio
            console.log 2
            radio.currentTime = current_time
          return null

  #track = get_random_track()
  track = PLAYLIST[0]
  set_track track, radio


get_random_track = () ->
  max = PLAYLIST.length - 1
  num_track = Math.floor(Math.random() * (max - 0 + 1)) + 0
  track = PLAYLIST[num_track]
  return track

set_track = (track, radio) ->
  if radio.canPlayType 'audio/ogg; codecs="vorbis"'
    radio.src = track.ogg
    if radio.duration == NaN
      radio.src = track.mp3
  else
    radio.src = track.mp3

  set_cookie 'radio_track_id', track.id
  #set_cookie 'radio_current_time', radio.currentTime
  radio.dataset.id = track.id

  console.log "NOW PLAYING: \"#{track.full_title}\""

get_cookie = (name) ->
  parts = document.cookie.split "#{name}="
  if parts.length == 2
    return parts.pop().split(";").shift()

  null

set_cookie = (name, value) ->
  document.cookie = name+"="+value+"; path=/"


get_from_cookies = () ->
  data = [null, null]
  id = get_cookie 'radio_track_id'
  current_time = get_cookie 'radio_current_time'
  if current_time
    data[0] = current_time
  if id
    data[1] = id

  data

next_track = (e) ->
  #track = get_random_track()
  max = PLAYLIST.length - 1
  current_track = this.dataset.id * 1
  for track in PLAYLIST
    if current_track == track.id
      next_track = _i + 1
  if next_track > max
    next_track = 0
  track = PLAYLIST[next_track]
  set_track track, this
  this.play()

$(document).on 'click', '#play_pause', play_pause

$('#radio').ready () ->
  radio = document.getElementById 'radio'
  radio.addEventListener 'ended', next_track
  state = get_cookie 'radio_pause'

  if state == "0"
    current_time = get_cookie 'radio_current_time'

    setTimeout (->
      now_current_time = get_cookie 'radio_current_time'
      diff = (now_current_time * 1.0) - (current_time * 1.0)

      if not diff
        console.log radio
        find_track radio
        console.log get_cookie 'radio_current_time'
        radio.currentTime = get_cookie 'radio_current_time'
        console.log radio.currentTime
        radio.play()
        $('#radio-img').attr 'src', '/static/img/radio_play.png'
        cron()
    ), 600