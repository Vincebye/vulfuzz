from colorama import Fore, Style
import datetime


class Log:
    # info_color='GREEN'
    # warn_color='YELLOW'
    # error_color='RED'
    # debug_color='BLUE'

    def warn(self, message):
        dt = datetime.datetime.now()
        print(
            Fore.YELLOW +
            Style.DIM +
            f'[{dt.hour}:{dt.minute}:{dt.second}]{message}')

    def info(
            self,
            message=None,
            code=None,
            hash=None,
            size=None,
            path=None,
            _302_url=None):
        dt = datetime.datetime.now()
        if code is None:
            print(
                Fore.GREEN +
                Style.BRIGHT +
                f'[{dt.hour}:{dt.minute}:{dt.second}]{message}')
        else:
            if code == 200:
                print(
                    Fore.GREEN +
                    Style.BRIGHT +
                    f'[{dt.hour}:{dt.minute}:{dt.second}]- {code} - {hash[0:7]} - {size}B -{path}')
            elif code in [401, 402, 403]:  # No 404
                print(
                    Fore.YELLOW +
                    Style.BRIGHT +
                    f'[{dt.hour}:{dt.minute}:{dt.second}]- {code} - {hash[0:7]} - {size}B -{path}')
            elif code in [500, 501, 502, 503]:
                print(
                    Fore.RED +
                    Style.BRIGHT +
                    f'[{dt.hour}:{dt.minute}:{dt.second}]- {code} - {hash[0:7]} - {size}B -{path}')
            elif code in [300, 301, 302, 303, 304]:
                print(
                    Fore.CYAN +
                    Style.BRIGHT +
                    f'[{dt.hour}:{dt.minute}:{dt.second}]- {code} - {size}B -{path}    -->     {_302_url} - {hash[0:7]}')
            elif code == 404:
                pass
            elif code==520:
                pass
            else:
                print(
                    Fore.RED +
                    Style.BRIGHT +
                    f'[{dt.hour}:{dt.minute}:{dt.second}]- {code} - 未知')

    def error(self, message):
        dt = datetime.datetime.now()
        print(
            Fore.RED +
            Style.BRIGHT +
            f'[{dt.hour}:{dt.minute}:{dt.second}]{message}')

    def debug(self, message):
        dt = datetime.datetime.now()
        print(
            Fore.GREEN +
            Style.BRIGHT +
            f'[{dt.hour}:{dt.minute}:{dt.second}]{message}')
