import customtkinter as ctk
from tkinter import messagebox
import threading
import requests
import time
from bs4 import BeautifulSoup
from win10toast import ToastNotifier

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class ProductChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("STOCK WATCH - Product Availability Checker")
        self.root.geometry("800x700")

        self.url_list = []
        self.product_details = {}

        self.title_frame = ctk.CTkFrame(root)
        self.title_frame.pack(pady = 10)

        #title
        self.title_label = ctk.CTkLabel(self.title_frame, text = "STOCK WATCH", font = ('Aerial', 24))
        self.title_label.pack()

        self.subtitle_label = ctk.CTkLabel(self.title_frame, text = "Product Availability Checker", font = ('Aerial', 14))
        self.subtitle_label.pack()

        #URL Entry
        self.url_entry = ctk.CTkEntry(root, width = 500)
        self.url_entry.pack()

        #Add URL button
        self.add_button = ctk.CTkButton(root, text = "Add URL", command = self.add_url)
        self.add_button.pack(pady = 5)

        self.url_frame = ctk.CTkFrame(root)
        self.url_frame.pack(pady = 10, fill = "both", expand = True)

        #URL list
        self.url_listbox = ctk.CTkTextbox(self.url_frame, width = 500, height = 100)
        self.url_listbox.pack(side = "left", fill = "both", expand = True)

        self.url_scrollbar = ctk.CTkScrollbar(self.url_frame, command = self.url_listbox.yview)
        self.url_scrollbar.pack(side = "right", fill = "y")
        self.url_listbox.configure(yscrollcommand = self.url_scrollbar.set)

        #Remove URL button
        self.remove_button = ctk.CTkButton(root, text = "Remove Selected URL", command = self.remove_url)
        self.remove_button.pack(pady = 5)

        #Details Output
        self.details_frame = ctk.CTkFrame(root)
        self.details_frame.pack(pady = 10, fill = "both", expand = True)

        self.details_text = ctk.CTkTextbox(self.details_frame, width = 800, height = 200)
        self.details_text.pack(side = "left", fill = "both", expand = True)

        self.details_scrollbar = ctk.CTkScrollbar(self.details_frame, command = self.details_text.yview)
        self.details_text.configure(yscrollcommand = self.details_scrollbar.set)

        #Web scraping
        self.start_periodic_scraping()

        self.toaster = ToastNotifier() #for pop-up notification
    
    def add_url(self):
        url = self.url_entry.get()
        if url:
            self.url_list.append(url)
            self.url_listbox.insert("end", url + '\n')
            self.url_entry.delete(0, "end")
            threading.Thread(target = self.scrape_data_and_notify, args = (url,)).start()
        else:
            messagebox.showwarning("Please enter a valid URL")
    
    def remove_url(self):
        selected_index = self.get_selected_line_index()
        print(selected_index)
        if selected_index is not None and selected_index < len(self.url_list):
            url = self.url_list.pop(selected_index)
            self.update_url_listbox()
            self.product_details.pop(url, None)
            self.update_details_text()
        else:
            messagebox.showwarning("Please select a URL to remove")
    
    def get_selected_line_index(self):
        try:
            index = self.url_listbox.index('insert').split('.')[0]
            return int(index) - 1  # Convert to zero-based index
        except Exception as e:
            print(f"Error getting selected line index: {e}")
            return None

    
    def update_url_listbox(self):
        self.url_listbox.delete("1.0", "end")
        for url in self.url_list:
            self.url_listbox.insert("end", url + "\n")
    
    def start_periodic_scraping(self):
        def scrape_loop():
            while True:
                time.sleep(5 * 3600)    #wait for 5 hours
                for url in self.url_list:
                    threading.Thread(target = self.scrape_data_and_notify, args = (url,)).start()
        threading.Thread(target = scrape_loop, daemon = True).start()   #automatically terminates when the program exits
    
    def scrape_data_and_notify(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Scraping required details from website
            product_name_elem = soup.find('span', attrs={'class': 'a-size-large product-title-word-break'})
            product_price_elem = soup.find('span', attrs={'class': 'a-price-whole'})
            product_discount_elem = soup.find('span', attrs={'class': 'a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage'})
            product_limited_deal_elem = soup.find('span', attrs={'class': 'a-size-small dealBadgeTextColor a-text-bold'})
            in_stock_elem = soup.find('span', attrs={'class': 'a-size-medium a-color-success'})
            stock_elem = soup.find('span', attrs={'class': 'a-size-base a-color-price a-text-bold'})

            # Initialize variables with default values
            product_name = "Not Found"
            product_price = "Not Found"
            product_discount = "No Discount"
            product_deal = "No Limited Time Deal"
            stock = "Out of Stock"

            # Assign values if elements are found
            if product_name_elem:
                product_name = product_name_elem.text.strip()

            if product_price_elem:
                product_price = product_price_elem.text.strip()

            if product_discount_elem:
                product_discount = product_discount_elem.text.strip()

            if product_limited_deal_elem:
                product_deal = product_limited_deal_elem.text.strip()

            if in_stock_elem:
                stock_text = in_stock_elem.text.strip()
                if "left in stock" in stock_text:
                    stock = int(''.join(filter(str.isdigit, stock_text)))   # Convert the text into integer
                else:
                    stock = "In Stock"

            # Store previous update before storing
            previous_details = self.product_details.get(url, {})

            # Update product details
            self.product_details[url] = {
                'name': product_name,
                'price': product_price,
                'discount': product_discount,
                'limited_deal': product_deal,
                'stock': stock
            }

            # Update GUI
            self.update_details_text()

            # Show notification based on changes
            if product_price != previous_details.get('price'):
                if previous_details.get('price') is None:
                    self.show_notification(f"{product_name}", f"Price : {product_price}")
                else:
                    self.show_notification("PRICE CHANGE!!", f"Product Price changed for {product_name}: \n {previous_details.get('price')} --> {product_price}")

            if product_discount != previous_details.get('discount'):
                if previous_details.get('discount') is None:
                    self.show_notification(f"{product_name}", f"Discount : {product_discount}")
                else:
                    self.show_notification("DISCOUNT CHANGE!!", f"Product Discount changed for {product_name}: \n {previous_details.get('discount')} --> {product_discount}")
            if product_deal != previous_details.get('limited_deal'):
                if product_deal == 'Limited time deal':
                    self.show_notification("HURRY!!, LIMITED TIME DEAL", f"{product_name}")
                else:
                    self.show_notification("Limited Time Deal Ended", f"{product_name}")

            if isinstance(stock, int) and stock <= 5:
                if stock == 1:
                    self.show_notification("WARNING!, Only 1 stock left!!", f"{product_name}")
                else:
                    self.show_notification(f"ALERT!, Low Stock!! \n Stock : {stock}", f"{product_name}")

        except Exception as e:
            print(f"Error scraping: {url}: {e}")

    
    def update_details_text(self):
        displayed_urls = set()
        self.details_text.delete(1.0, "end")
        for url, details in self.product_details.items():
            if url not in displayed_urls:
                info = (
                    f"Name : {details['name']}\n"
                    f"Price : {details['price']}\n"
                    f"Discount : {details['discount']}\n"
                    f"Deals : {details['limited_deal']}\n"
                    f"Stock : {details['stock']}\n\n"
                )
                self.details_text.insert("end", info)
                displayed_urls.add(url)
    
    def show_notification(self, title, message):
        self.toaster.show_toast(title, message, duration = 3)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ProductChecker(root)
    root.mainloop()