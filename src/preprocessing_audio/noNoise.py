import ffmpeg

from os   import system, path, listdir, chdir, mkdir
from sys  import argv
from time import sleep

def checkType():
    #Check for type of first argument(file or dir).
    if path.isdir(argv[1]):
        processDir()
    else:
        processFile()
    return


def processDir():
    #make dir to save all new files
    mkdir(argv[2])
    #cd to source dir   
    chdir(argv[1])
    for eachfile in listdir('.'):
        execute(setCommands(eachfile))
    return


def processFile():
    #Calling setCommands with source file.
    #Will return list of commands to be executed
    execute(setCommands(argv[1]))
    return
    

def execute(cli):     
    #total 7 commands with some delay for disk
    #write and sync    
    for each in cli:
        system(each)
        sleep(0.2)
    return    


def setCommands(filename):
     #The dirty function.        
     cli = [None]*7
     cli[0] = 'ffmpeg -i ' + ' ' + filename + ' -qscale 0 ' + '.rawVideo.wmv'
     cli[1] = 'ffmpeg -i ' + ' ' + filename + ' -qscale 0 ' + '.rawAudio.wav'
     cli[2] = 'sox .rawAudio.wav -t null /dev/null trim 0 0.5 noiseprof myprofile'
     #Checks for noise factor.
     if len(argv)>3:
         cli[3] = 'sox .rawAudio.wav .noisefree.wav noisered myprofile ' + argv[3]
     else:
         #The default value for noise factor is 0.26. Change accordingly.   
         cli[3] = 'sox .rawAudio.wav .noisefree.wav noisered myprofile 0.26'
     #Creating a less compressed file to retain video quality.
     cli[4] = 'ffmpeg -i .noisefree.wav -i .rawVideo.wmv -qscale 0 .combined.wmv'
     #Checks for file or directory. If dir, the output is saved in different directory.
     if not path.isfile(argv[1]):
         cli[5] = 'ffmpeg2theora .combined.wmv -o ' + '../' + argv[2] + '/' + filename
     else:
         #Will create the final ogv video from wmv.
         cli[5] = 'ffmpeg2theora .combined.wmv -o ' + argv[2]
     cli[6] = 'rm .rawVideo.wmv .rawAudio.wav .noisefree.wav .combined.wmv myprofile'
     return cli



if __name__ == '__main__':



     checkType()
