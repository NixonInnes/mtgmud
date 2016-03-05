def colourify(string):
    # This feels kinda janky...
    # TODO: make this nicer
    string += "&x"
    # Foreground
    string=string.replace('&b', '\033[30m') #black
    string=string.replace('&r', '\033[31m') #red
    string=string.replace('&g', '\033[32m') #green
    string=string.replace('&y', '\033[33m') #yellow
    string=string.replace('&u', '\033[34m') #blue
    string=string.replace('&m', '\033[35m') #magenta
    string=string.replace('&c', '\033[36m') #cyan
    string=string.replace('&w', '\033[37m') #white
    string=string.replace('&x', '\033[39m') #reset
    return string