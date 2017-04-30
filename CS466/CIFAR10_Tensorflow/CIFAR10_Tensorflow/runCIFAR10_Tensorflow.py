from cifar10_train import main as run_cifar10_train
from cifar10_eval import main as run_cifar10_eval, tf
from PythonVersionHandler import *
from paths import *

def printSeparater():
    for n in range(3):
        print_('#' * 88)
        
def main(method = None):
    printSeparater()
    print_('%s:' % nowStr(), 'Running on', os.getenv('COMPUTERNAME') + '...')
    
    if method == None:
        run_cifar10_train()
        run_cifar10_eval()
    else:
        method()

    print_('%s:' % nowStr(), 'DONE')
    printSeparater()

    sys.exit() 

if __name__ == "__main__":
    main()