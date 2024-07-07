# Stock-Watch
Amazon product availability checker

An Amazon product availability checker which checks the details of a product using URL link and update you time-to-time about the changes of your tracked products.

It checks the product price, discount, number of stocks. It pops up a notification on your Windows regarding any changes made in the product. 

For example, if there is less than 5 stocks or only 1 stock left, it notify you about your listed product that Hurry!, Only 1 stock is left!. It also notify if there is change in price or discount.

It has option to remove or add any product URL as you want and checks every listed items every 5 hours for any update.

![Screenshot (76)](https://github.com/divakshu04/Stock-Watch/assets/127183494/76ed9086-d78c-47ea-adb5-28132985e6e7)


## Installation

Install 'Python' and following modules:

```bash
  pip install customtkinter
  pip install tkinter
  pip install requests
  pip install bs4
  pip install win10toast
```
The 'requests' module is used to make requests while web scraping and 'win10toast' for providing notification especially on Windows.
