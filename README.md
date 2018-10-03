# domino
Python IRC Server - IRCd with services. It's kind of useless. It's also kind of fun. One day domino will be a full-featured IRC server, for now it's just a playground.

**You can join my home server if you're interested by the project: home.fy.to:6667, I'll debug live ^_^**

## install
```
pip install -r requirements.txt
py run.py #: edit config dict (oper password with werkzeug.security.generate_password_hash)
```

## services
```
-NickServ-  NickServ allows you to register a nickname.
-NickServ- 	GHOST     /msg nickserv ghost <nick> <pass>     Kill someone with your nickname.
-NickServ- 	IDENTIFY  /msg nickserv identify <pass>         Identify yourself.
-NickServ- 	REGISTER  /msg nickserv register <pass> <mail>  Register your current nickname
-NickServ- 	
  
-ChanServ-  ChanServ allows you to register a channel.
-ChanServ- 	REGISTER  /msg chanserv register <channel>      Register a channel.

privmsg #chan commands: !op !deop !topic !voice !devoice !voiceall !owner !strip !kick ^_^
```


## Unique features
Extensions are not active with the new version, please be patient.
__1. OperServ name is Loki:__
Best feature ever.

__2. Best hostnames ever:__ Using markov chains and MCU Subtitles
```
  @when.you.save.the.world.proxad.net
```

__3. Server side smileys: (stupid concept)__
```
 ':(': '😒', ':)': '😊', ':D': '😃', '>.<'  : '😆', '^^': '😄', ':|': '😐', ':p': '😋', '=)': '㋡', '<3': '❤', ':x': '☠', '(note)'  : '♫', '(mail)'  : '✉', '(star)'  : '✩', '(valid)' : '✔', '(flower)': '❀', '(plane)' : '✈', '(copy)'  : '©', '(tel)'   : '☎', 'x.x'  : '٩(×̯×)۶', 'o.o'  : 'Ꙩ_Ꙩ', '<3.<3' : '❤‿❤'
```
