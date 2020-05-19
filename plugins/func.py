from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
import sys, subprocess, os.path, os, glob, time
from .cfg import * # 同じ階層のcfg.pyからimport
from PIL import Image

@listen_to('!exit') # 使い物にならない関数
def kill_process(message):
    message.send('See you!')
    print('process finished')
    sys.exit()

@listen_to('!output (.*)')
def output(message, arg): # argはオプション
    # 送信されたテキストを整形
    tmp = message.body['text']
    tmp = tmp.replace("&lt;", "<")
    tmp = tmp.replace("&gt;", ">")

    pdeCode = shaping_code(tmp.strip("!output " + arg + "\n"), arg) # pde上書き用の文字列に整形
    #print(pdeCode)
    message.send('wait...')

    print(pdeCode)
    # pdeに上書き
    f = open('sketch/sketch.pde', 'w')
    f.write(pdeCode)
    f.close()

    cp = subprocess.run(['processing-java',  sketch_path, '--run']) # cfg.pyファイルからスケッチまでの絶対パスを入手
    if cp.returncode != 0:
        message.send('Run is failed.')
        sys.exit(1)
    
    upload_sequence(message, arg)

def shaping_code(code, option):
    if option == '--png': # pngオプション
        pictFunc = "  if((frameCount <= 15) && (frameCount % 15 == 0)) saveFrame(\"####.png\");\n  else if(frameCount > 15) exit();"
    else: # デフォルトの動画オプション
        pictFunc = "  if((frameCount <= 300) && (frameCount % 15 == 0)) saveFrame(\"####.png\");\n  else if(frameCount > 300) exit();"
    return code.replace("void draw(){", "void draw(){\n" + pictFunc)

def upload_sequence(message, option):
    if option == '--png':
        message.channel.upload_file(fname="sketch/0015.png", fpath="sketch/0015.png")
        if os.path.exists('sketch/0015.png'):
            os.remove('sketch/0015.png')
    elif option == '--gif':
        time.sleep(6)
        file_list = sorted(glob.glob('sketch/*.png'))  
        images = list(map(lambda file : Image.open(file) , file_list))
        images[0].save('sketch/output.gif' , save_all = True , append_images = images[1:] , duration = 400 , loop = 0)
        if os.path.exists('sketch/output.gif'):
            message.channel.upload_file(fname="sketch/output.gif", fpath="sketch/output.gif")
            for p in glob.glob('sketch/*.png'):
                if os.path.isfile(p):
                    os.remove(p)
            os.remove('sketch/output.gif')


