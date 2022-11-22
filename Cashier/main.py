import os
import logging
import td_ameritrade

from dotenv import load_dotenv

def main():
    print('running TD Ameritrade API')
    load_dotenv()  # load environment variables from .env file
    log_file = os.getenv('LOG_FILE')
    print(f'See {log_file} for more details.')
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    td_ameritrade.auth()


if __name__ == '__main__':
    main()