# yield.credit Stats Bot (Telegram Front End)


A Telegram bot that produces merchandise for the cryptocurrency 'YLD' on demand.
You can add this bot on Telegram by searching for its handle `@ (to be published)`.
Send it a command and it sends back infographics with always up-to-date
metrics, i.e. current usage statistics for the platform yield.credit, or a personal impermanent loss graph vs. time, based on the user's pool entry date.


Here is an example of one of the infograpics the bot delivers. So far this is obviously still a work in progress:

![Preview](https://github.com/al-matty/yield-stats-bot/blob/main/loans.png)

## Requirements & Installation

The script runs on `python 3` and uses the packages listed in `requirements.txt`. 

The best practice would be to install a virtual environment and install the
requirements afterwards using `pip`:
```
pip3 install -r requirements.txt
```
If you're using `conda`, you can create a virtual environment and install the
requirements using this code:

```
conda create -n statsbot python=3.6
conda activate statsbot
pip3 install -r requirements.txt
```

## License

This project is licensed under the [MIT license](https://github.com/al-matty/yield-stats-bot/blob/main/LICENSE) - see the [LICENSE](https://github.com/al-matty/yield-stats-bot/blob/main/LICENSE) file for details.
