import collections.abc
from typing import Optional, Any, Union, Iterable
import sys
import codecs
import collections
import time
import shutil
import signal
from multiprocessing import Lock
import datetime

lock = Lock()
try:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
except:
    pass


############################################
##::::::::::::::::::::::::::::::::::::::::##
##::                                    ::##
##::           GENERAL TOOLBOX          ::##
##::                                    ::##
##::::::::::::::::::::::::::::::::::::::::##
############################################

MODS = set()
_DEBUG_MOD_KEY = "debug"
_SHOW_DATE_MOD_KEY = "show_date"
_ALWAYS_LOG_MOD_KEY = "always_log"


_ALWAYS_LOG_FILE = "last_logs.txt"

###### COLORS

RESET_COLOR = "\33[0m"
RED_COLOR = "\33[91m"
GREEN_COLOR = "\33[92m"
ORANGE_COLOR = "\33[33m"
LIGHT_BLUE_COLOR = "\33[36m"
ERASE_LINE_COLOR = "\33[2K"
BLUE_COLOR = "\33[34m"
ITALIC_COLOR = "\u001b[3m"
BOLD_COLOR = "\u001b[1m"
UNDERLINE_COLOR = "\u001b[4m"

def get_text_color(R,G,B):
    return "\u001b[38;2;"+str(R)+";"+str(G)+";"+str(B)+"m"

def get_back_color(R,G,B):
    return "\u001b[48;2;"+str(R)+";"+str(G)+";"+str(B)+"m"

#####################


def _str_move_cursor_up(n:int):
    return "\033["+str(n)+"A"

def _str_move_cursor_down(n:int):
    return "\033["+str(n)+"B"

def beautiful_print(*values: object,
                    color:Optional[str]=None,
                    erase_current_line:bool=True,
                    go_up:int=0,
                    mod=None,
                    max_char=-1,
                    log=None,
                    log_only=False,
                    show_date=False,
                    no_log_ffs=False,
                    **params):
    
    size = shutil.get_terminal_size(fallback=(80, 24))
    cols, lines = size.columns, size.lines
    
    if not is_mod_enabled(mod):
        return
    
    values2 = list([str(s) for s in values])
    show_date = show_date or is_mod_enabled(_SHOW_DATE_MOD_KEY)
    if show_date:
        now = datetime.datetime.now()
        values2.insert(0, f"[{now}]")
    
    if len(values2) == 0:
        values2.append("")
    
    if erase_current_line:
        values2[0] = ERASE_LINE_COLOR + str(values2[0])
    
    if go_up > 0:
        values2[0] = _str_move_cursor_up(go_up) + str(values2[0])
        
    if color != None:
        values2[0] = color + str(values2[0])
        
    values2[-1] = str(values2[-1]) + RESET_COLOR
    
    if go_up > 0:
        values2[-1] = str(values2[-1]) + _str_move_cursor_down(go_up)
    
    if max_char > 0:
        values3 = []
        size = 0
        for val in values2:
            size += len(val) + 1
            if size >= max_char:
                values3.append(val[:-(max_char-size+1)])
                break
            values3.append(val)
        values2 = values3
        
    values2 = (" ".join([str(s) for s in values2]))[:cols-1]
    
    if not log_only:
        if go_up > 0:
            with lock:
                print(values2, end='\r', flush=True, **params)
        else:
            with lock:
                print(values2, flush=True, **params)
    
    if not no_log_ffs:      
        log = log or is_mod_enabled(_ALWAYS_LOG_MOD_KEY) and _ALWAYS_LOG_FILE
        if log:
            try:
                now = datetime.datetime.now()
                with open(log, "a", encoding="utf-8") as log_file:
                    if show_date:
                        log_file.write(f"{str(values2)}\n")
                    else:
                        log_file.write(f"[{now}] {str(values2)}\n")
                        
                    log_file.flush()
            except Exception:
                pass

def rainbow_text(text, colors):
    if len(colors)==0:
        return text
    returned = ""
    for i,c in enumerate(text):
        returned += colors[i%len(colors)] + c
    return returned

def enable_debug(enable=True):
    global MODS
    if enable:
        MODS.add(_DEBUG_MOD_KEY)
    else:
        MODS.remove(_DEBUG_MOD_KEY)
        
def is_mod_enabled(mod):
    if mod:
        return (mod in MODS)
    return True

def is_debug_enabled():
    global MODS
    return is_mod_enabled(_DEBUG_MOD_KEY)

def enable_mod(mod):
    global MODS
    MODS.add(mod)
    
def disable_mod(mod):
    global MODS
    if mod in MODS:
        MODS.remove(mod)

def debug_print(*values: object):
    global MODS
    
    if not is_debug_enabled():
        return
    
    if not values:
        print()
        return
    
    back_color = get_back_color(255,69,0)
    debug_txt = rainbow_text("DEBUG",[get_text_color(255,255,0),get_text_color(0,255,255),get_text_color(255,0,255)])+RESET_COLOR+back_color
    beautiful_print(back_color+"["+debug_txt+"]",*values)

def always_show_date(enable=True):
    enable_mod(_SHOW_DATE_MOD_KEY) if enable else disable_mod(_SHOW_DATE_MOD_KEY)
    
def always_log(enable=True, log_file="last_logs.txt"):
    enable_mod(_ALWAYS_LOG_MOD_KEY) if enable else disable_mod(_ALWAYS_LOG_MOD_KEY)
    global _ALWAYS_LOG_FILE
    _ALWAYS_LOG_FILE = log_file
    
####################



def get_progression(current : float,
                    total : float,
                    length : int = 40,
                    filled_str: str="▬",
                    empty_str: str="─",
                    left_separator=RESET_COLOR+"["+LIGHT_BLUE_COLOR,
                    right_separator=RESET_COLOR+"]",
                    progress_separator=BLUE_COLOR) -> str:
    """
    DESCRIPTION\n
    Returns some progression string, like tqdm but worse\n
    - current is the current advancement of the process\n
    - total is the max advancement possible for the process\n
    - length is the length of the returned progressbar (20 = 20 char)\n
    - filled_str is the char to print on the left side of the bar (where progression has occured)\n
    - empty_str is the char to print on the right side of the bar (where progression has not occured yet)\n
    - left_separator is the string to print at the left of the progressbar (default : '[')\n
    - right_separator is the string to print at the right of the progressbar (default : ']')\n
    - progress_separator is the string to print at the center of the progressbar (default : '')\n
    RETURNS : The string of the progressbar to print
    """
    nb = round(length*current/total)
    return left_separator+(nb*filled_str)+progress_separator+((length-nb)*empty_str)+right_separator

def print_progressbar(current : float,
                      total : float,
                      pre_string : str="",
                      post_string : str="",
                      length : int=40,
                      filled_str: str="▬",
                      empty_str: str="─",
                      left_separator=RESET_COLOR+"["+LIGHT_BLUE_COLOR,
                      right_separator=RESET_COLOR+"]",
                      progress_separator=BLUE_COLOR,
                      print_digits=True,
                      print_percentage=True,
                      go_up:int=1,
                      unit:str="",
                      mod=None) -> None:
    """
    DESCRIPTION\n
    prints some progression string, like tqdm but worse\n
    - pre_string is the string to print before the progressbar\n
    - current is the current advancement of the process\n
    - total is the max advancement possible for the process\n
    - post_string is the string to print after the progressbar\n
    - length is the length of the returned progressbar (20 = 20 char)\n
    - filled_str is the char to print on the left side of the bar (where progression has occured)\n
    - empty_str is the char to print on the right side of the bar (where progression has not occured yet)\n
    - left_separator is the string to print at the left of the progressbar (default : '[')\n
    - right_separator is the string to print at the right of the progressbar (default : ']')\n
    - progress_separator is the string to print at the center of the progressbar (default : '')\n
    - print_digits is True if you want to print the progress after the progressbar. exemple : "(90/100)"
    - print_percentage is True if you want to print the progress (percentage mode) after the progressbar. exemple : "90%"
    - go_up is the number of lines you go up to print the progressbar (default = 1, updates the last line)
    - mod is the name of a mod that must be enabled to print the progressbar
    
    """
    
    if not is_mod_enabled(mod):
        return
    
    progress = get_progression(current=current, total=total, length=length, filled_str=filled_str, empty_str=empty_str, left_separator=left_separator, progress_separator=progress_separator, right_separator=right_separator)
    
    if print_digits:
        progress += f" ({current}{unit}/{total}{unit})"
    if print_percentage:
        progress += f" {round(100*current/total)}%"
        
    to_print = pre_string + progress + post_string
    
    beautiful_print(to_print+RESET_COLOR, color=RESET_COLOR, go_up=go_up, no_log_ffs=True)

##################

def prompt(
    *values,
    options:Optional[Iterable[Union[str,Iterable[str]]]]=["y","n"],
    show_options:bool=True,
    wrong_prompt_msg:Optional[str]=None,
    case_sensitive:bool=False,
    default:Optional[Any]=None,
    **params) -> Union[int,str]:
    """
    DESCRIPTION\n
    Repetitive prompt. Asks the user for an input until its in proposed options\n
    - options is the list of allowed options (an option is either a string, or a list of similar strings that will return the same index).\n
    - show_options shows the list of options allowed to user if true\n
    - wrong_prompt_msg is the msg showed to user if user prompt not in options\n
    - case_sensitive speaks by itself\n
    
    """
    
    if options == None:
        beautiful_print(*values, **params)
        return input()
    
    showed_options = []
    for option in options:
        if isinstance(option, str):
            showed_options.append(option)
        elif isinstance(option, collections.abc.Iterable):
            showed_options.append(list(option)[0])
        else:
            raise ValueError("options must only contain str or iterable")
    
    while True:
        if show_options:
            beautiful_print(*values, "("+(",".join(showed_options))+")", **params)
        else:
            beautiful_print(*values, **params)
        ans = input()
        if ans == "" and default != None:
            return default
        for i,option in enumerate(options):
            if case_sensitive:
                if (isinstance(option, str) and option == ans) or (isinstance(option, collections.abc.Iterable) and ans in option):
                    return i
            else:
                if (isinstance(option, str) and option.lower() == ans.lower()) or (isinstance(option, collections.abc.Iterable) and ans.lower() in {s.lower() for s in option}):
                    return i
                
        if wrong_prompt_msg:
            beautiful_print(wrong_prompt_msg, color=RED_COLOR)





############################################
##::::::::::::::::::::::::::::::::::::::::##
##::                                    ::##
##::               MAIN.                ::##
##::                                    ::##
##::::::::::::::::::::::::::::::::::::::::##
############################################



    
#Test main function
if __name__ == '__main__':
    
    P1_END = 100
    P2_END = 1000
    P3_END = 200
    
    ALL_P_END = max(P1_END,P2_END,P3_END)+1
    
    import time
    # Jumps 3 lines for the 3 progressbars
    print()
    print()
    print()
    
    #Fake process
    for i in range(1,ALL_P_END):
        
        P1_STATUS = min(i, P1_END)
        P2_STATUS = min(i, P2_END)
        P3_STATUS = min(i, P3_END)
        
        print_progressbar(P1_STATUS, P1_END, go_up = 3, pre_string = (RED_COLOR + "Process #1 "))
        print_progressbar(P2_STATUS, P2_END, go_up = 2, pre_string = (ORANGE_COLOR + "Process #2 "))
        print_progressbar(P3_STATUS, P3_END, go_up = 1, pre_string = (BLUE_COLOR + "Process #3 "))
        
        """
        # Alternative version :
        
        beautiful_print("Process #1", get_progression(min(i, 100), 100),str(min(i, 100))+"%", color = RED_COLOR, go_up = 3)
        beautiful_print("Process #2", get_progression(min(i, 1000), 1000),str(min(i // 10, 100)) + "%", color = ORANGE_COLOR, go_up = 2)
        beautiful_print("Process #3", get_progression(min(i, 200), 200),str(min(i // 2, 100)) + "%", color = GREEN_COLOR, go_up = 1)
        """
        
        time.sleep(0.1)