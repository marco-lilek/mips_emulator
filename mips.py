import sys
from machine import MipsMachine

def args_to_dict(args):
    args_len = len(args)
    if args_len < 2:
        raise Exception('bad number of arguments')

    valid_types = ['twoints', 'array', 'noinp']
    if args[0] not in valid_types:
        raise Exception('unknown argument {0}'.format(args[0]))

    options = {'type' : args[0], 'filename': args[1], 'display': False, 'memory':1000, 'start':0}
    ind = 2
    while ind < args_len:
        if args[ind] == '-d':
            options['display'] = True
            ind += 1
        elif args[ind] == '-m':
            options['memory'] = int(args[ind + 1])
            ind += 2
        elif args[ind] == '-s':
            options['start'] = int(args[ind + 1])
            ind += 2
        else:
            raise Exception('unknown argument {0}'.format(args[ind]))
    return options

def main(args):
    try:
        options = args_to_dict(args)
    except Exception as e:
        print(e)
        print('mips.py twoints|array|noinp <filename> [-d] [-m <# words>] [-s <start addr>]')
        return

    machine = MipsMachine(options['memory'])
    machine.run(options['type'], options['filename'], options['start'], True) #options['debug']
    machine.print_results(options['display'])

if __name__ == "__main__":
    main(sys.argv[1:])


