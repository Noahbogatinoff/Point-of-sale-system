import datetime
import sqlite3
import random
import pickle
#now = datetime.datetime.now()
#define class to refence in online orders
class Item:

    def __init__(self, upc, description, price):
        self.__upc = upc
        self.__description = description
        self.__price = price

    def get_upc(self):
        return self.__upc

    def get_description(self):
        return self.__description

    def get_price(self):
        return self.__price
#displays menu for the users to interact with
def main():
    print("Enter the number of the desired action\n")
    print("1. In store purchase\n")
    print("2. Online order\n")
    print("3. Add items\n")
    print("4. Add items through csv file\n")
    print("5. Quit\n")
    option = input(">> ")
    if option == "1":
        in_store()
    elif option == "2":
        online_order()
    elif option == "3":
        add_items()
    elif option == "4":
        add_items_csv()

#function inidcates an in store purchase
def in_store():
    new_cust = "y"
    items = csv_to_list()
    #prompt the user to indicate whether more customers are present
    while new_cust == "y":
        in_store_run(items)
        new_cust = input("Is there a new customer? (y/n): ")

#creates main function for an in-store purchase
def in_store_run(items):
    id_num = get_id()
    purchased_items = purchase(items)
    totals = sale_total(purchased_items)
    file_receipt(totals, id_num)
    date = str(datetime.datetime.now())
    sales_to_db(date, id_num, purchased_items)
#generates ID num for each customer based on time stamp
def get_id():
    id = str(datetime.datetime.now())
    id = id[0:4] + id[5:7] + id[8:10] + id[11:13] + id[14:16] + id[17:19]
    return id
#creates main function for the online order section
def online_order():
    pickle_in = open("order.pickle", "rb")
    online_order = pickle.load(pickle_in)
    id_num = get_id()
    totals = sale_total(online_order)
    file_receipt(totals, id_num)
    date = str(datetime.datetime.now())
    sales_to_db(date, id_num, online_order)
#converts the csv file of UPCs to list and adds them to a new database 
def add_items():
    keep_going = "y"
    while keep_going == "y":
        upc = input("What is the new UPC? ")
        description = input("What is the new item description? ")
        price = random.uniform(.99,4.99)
        new_item = Item(upc, description, price)
        item_to_db(new_item)
        keep_going = input("Do you want to add a new item? (y/n): ")
#function that allows user to add new items into database
def add_items_csv():
    print("Adding items from UPC_data.csv to the item database")
    item_list = csv_to_list()
    for item in item_list:
        item_to_db(item)
    print("New items added")
    
#converts the csv file of UPCs to list
def csv_to_list():
    # read in the csv file to a list
    infile = open('UPC_data.csv', 'r',encoding='utf-8-sig')
    items = []
    for line in infile:
        item = line.rstrip('\n').split(',')
        price = random.uniform(.99,4.99)
        item = Item(item[1], item[2], price)
        items.append(item)
        print(item.get_upc() + " " + item.get_description())
        #print the list to display UPCs and descriptions
    return items
#prompt user to indicate if new items are being purchased, enter input
#and create list of purchaed items
def purchase(items):
    keep_going = "y"
    purchased_items = []
    while keep_going == "y":
        UPC = input("Enter UPC: ")
        # Go through items and find wanted UPC, get description at index 2
        item = get_item_from_db(UPC)
        if item == -1:
            print("UPC not found")
        else:
            purchased_items.append(item)
        keep_going = input("Is there another item? (y/n): ")
    return purchased_items
#retreives the current items in the list based off UPC and
#gives the description and price
def get_item_from_db(UPC):
    conn = sqlite3.connect("store.db")
    c = conn.cursor()  
    string = "SELECT Description FROM items WHERE UPC = ?"
    c.execute(string, (UPC,))
    description = c.fetchall()
    string = "SELECT Price FROM items WHERE UPC = ?"
    c.execute(string, (UPC,))
    price = c.fetchall()
    #close the file
    conn.close()
    if len(description) != 0 and len(price) != 0:
        return Item(UPC, description[0][0], price[0][0])
    else:
        return -1

#calculates subtotal, tax, grand total and diplays for user
def sale_total(purchased_items):
    subtotal = 0
    # For each item generate a random price and add it to the subtotal
    for item in purchased_items:
        subtotal += item.get_price()
    print("Subtotal: $", format(subtotal, ".2f"))
    tax = subtotal * 0.08
    print("Tax: $", format(tax, ".2f"))
    g_total = subtotal + tax
    print("Grand Total: $", format(g_total, ".2f"))
    return subtotal, tax, g_total


#saves purchase info into file of receipt history
def file_receipt(totals, id_num):
    outfile = open("receipt_history.txt", "a")
    outfile.write("Customer " + str(id_num) + '\n')
    outfile.write("Subtotal: {:.2f}  ".format(totals[0]))
    outfile.write("Tax: {:.2f}  ".format(totals[1]))
    outfile.write("Grand Total: {:.2f}  \n\n".format(totals[2]))
    outfile.close()


#create sqlite3 databse that saves UPCs and ID numbers into the database
def sales_to_db(date, id_num, purchased_items):
    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    
    # Create table for purchases
    c.execute("""CREATE TABLE IF NOT EXISTS sales
                 (ID,
                  Date,
                  UPC,
                  Description,
                  Price);""")
    

    for item in purchased_items:
        #Insert row of data
        string = "INSERT INTO sales(ID, Date, UPC, Description, Price) VALUES (?,?,?,?,?)"
        c.execute(string, (id_num, date, item.get_upc(), item.get_description().replace("\"", ""), format(item.get_price(), ".2f")))

    #commit the changes
    conn.commit()
    
    #close the file
    conn.close()

#saves the itmes of UPC and descriptions to datbase
def item_to_db(item):
    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    
    # Create table for initial items list
    c.execute("""CREATE TABLE IF NOT EXISTS items
                 (UPC,
                  Description,
                  Price);""")
    
    string = "INSERT INTO items(UPC, Description, Price) VALUES (?,?,?)"
    c.execute(string, (item.get_upc(), item.get_description(), item.get_price()))

    #commit the changes
    conn.commit()
    
    #close the file
    conn.close()

main()
