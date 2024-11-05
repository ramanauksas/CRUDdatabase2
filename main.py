import random
import datetime
from decimal import Decimal
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port="3309",
    user="root",
    password="root",
    database="shop2"
)
c = conn.cursor()




def print_info():
    print("---------------------------------")
    print("1. Prekių nomenklatūros atvaizdavimas")
    print("2. Naujos prekės sukūrimas")
    print("3. Prekės redagavimas")
    print("4. Prekės šalinimas")
    print("5. Sandėlio pildymas")
    print("6. Prekės pardavimas")
    print("7. Išeiti iš programos")
    # print("6. Populiariausia prekė")
    # print("7. Daugiausiai pelno sugeneravusi prekė")
    # print("8. Periodo ataskaita")
    # print("9. Įšaldytos lėšos")
    # print("10. Atsargų vertė rinkos kainomis")
    # print("11.Prognozuojamas pelnas, išpardavus atsargas")
    # print("12.Išeiti iš programos")

def print_items():
    query = "SELECT * FROM items"
    c.execute(query)
    items = c.fetchall()
    if len(items) == 0:
        print("Prekių kol kas nėra įkelta.")
    else:
        [print(item) for item in items]
    return items

def add_item():
    title = input("Prekės pavadinimas: ")
    query = f"INSERT INTO `items`(`title`) VALUES (%s)"
    c.execute(query, (title,))
    conn.commit()

def get_item(id):
    query = f"SELECT * FROM items WHERE id = {id}"
    c.execute(query)
    res = c.fetchone()
    item = dict(
        id=res[0],
        title=res[1],
        total_quantity=res[2],
        current_price=res[3]
    )
    return item

def edit_item():
    item_id = input("Nurodykite prekės, kurią redaguosite, ID: ")
    item = get_item(item_id)
    print(item)
    title = input("Prekės pavadinimas: ")
    title = title if title else item['title']
    query = f"UPDATE `items` SET `title`=%s WHERE `id`=%s"
    c.execute(query, (title, item_id))
    conn.commit()


def delete_item():
    item_id = input("Nurodykite prekės, kurią norite šalinti, ID: ")
    query = "DELETE FROM `items` WHERE `id` = %s"
    c.execute(query, (item_id, ))
    conn.commit()

def purchase_inventory(items):
    item_ids = [item[0] for item in items]
    item_id = int(input("Nurodykite prekės, kurią norite pirkti, ID: "))
    if item_id not in item_ids:
        print("Prekės su tokiu ID nėra")
        return

    stop_buying = False
    while not stop_buying:
        item = get_item(item_id)
        print(item)

        quantity = int(input(f"Iveskite perkamų atsargų kiekį (arba 0, jei norite nutraukti įvedimą): "))
        if quantity == 0:
            stop_buying = True
            continue

        # add a new record to purchase_log table
        price = float(input(f"Įveskite prekės vieneto savikainą: "))
        created_at = datetime.datetime.now()
        purchase_query = f"INSERT INTO `purchase_log` (`item_id`, `quantity`, `price`, `created_at`) VALUES (%s,%s,%s,%s)"
        c.execute(purchase_query, (item_id, quantity, price, created_at))

        # update quantity and current_price in items table
        total_quantity = item['total_quantity'] + quantity
        current_price = price
        item_query = f"UPDATE `items` SET `total_quantity`=%s,`current_price`=%s WHERE `id`=%s"
        c.execute(item_query, (total_quantity, current_price, item_id))

        conn.commit()


def sell_product(items):
    item_ids = [item[0] for item in items]
    item_id = int(input("Nurodykite parduodamos prekės ID: "))
    if item_id not in item_ids:
        print("Prekės su tokiu ID nėra")
        return

    stop_selling = False
    while not stop_selling:
        item = get_item(item_id)
        print(item)
        quantity = int(input(f"Iveskite parduodamų prekių kiekį (maks. {item['total_quantity']}), arba įveskite 0, jei norite nutraukti įvedimą: "))
        if quantity == 0 or item['total_quantity']==0:
            stop_selling = True
            continue

        # add a new record to payments table
        unit_price = float(input(f"Įveskite parduodamos prekės kainą: "))
        created_at = datetime.datetime.now()
        sale_query = f"INSERT INTO `payments` (`item_id`, `quantity`, `unit_price`, `created_at`) VALUES (%s,%s,%s,%s)"
        c.execute(sale_query, (item_id, quantity, unit_price, created_at))

        # update quantity in items table
        total_quantity = item['total_quantity'] - quantity
        item_query = f"UPDATE `items` SET `total_quantity`=%s WHERE `id`=%s"
        c.execute(item_query, (total_quantity, item_id))

        # insert new record in price_log table
        price_query = f"INSERT INTO `price_log`(`item_id`, `price`, `created_at`) VALUES (%s,%s,%s)"
        c.execute(price_query, (item_id, unit_price, created_at))

        conn.commit()


while True:
    print_info()
    choice = input()

    match choice:
        case '1':
            print_items()
        case '2':
            add_item()
            pass
        case '3':
            print_items()
            edit_item()
            pass
        case '4':
            delete_item()
        case '5':
            items = print_items()
            purchase_inventory(items)
            pass
        case '6':
            items = print_items()
            sell_product(items)
        case '7':
            exit()
        # case '6':
        #     most_popular_item()
        # case '7':
        #     most_profitable_item()
        # case '8':
        #     sales_report()
        # case '9':
        #     inventory_cost()
        # case '10':
        #     inventory_at_market_prices()
        # case '11':
        #     expected_profits()
        # case '12':
        #     exit()








#
# def get_random_date():
#     start_date = datetime.datetime(2022,1,1)
#     end_date = datetime.datetime(2024,12,31)
#     delta = end_date - start_date
#     rand_delta = datetime.timedelta(days=random.randint(0, delta.days))
#     rand_date = start_date + rand_delta
#     return rand_date
#
# def buy_item():
#     item_id = input("Nurodykite prekės, kurią norite pirkti, ID: ")
#
#     stop_buying = False
#     while not stop_buying:
#         item = get_item(item_id)
#         print(item)
#         rand_sale_price = item['sale_price'] + random.randint(-20,20) * Decimal('0.01')
#         rand_date = get_random_date()
#         print(f"{rand_date.strftime("%Y-%m-%d")} dienos rinkos kaina: {rand_sale_price}")
#
#         manufacturer_price = item['manufacturer_price']
#         quantity = int(input(f"Iveskite perkamos prekės kiekį (max. {item['quantity']}) arba 0, jei norite nutraukti įvedimą: "))
#
#         if quantity == 0 or item['quantity']==0:
#             stop_buying = True
#             continue
#
#         payment_query = f"INSERT INTO `payments`(`item_id`, `quantity`, `manufacturer_price`, `sale_price_per_unit`, `created_at`) VALUES (%s,%s,%s,%s, %s)"
#         c.execute(payment_query, (item_id, quantity, manufacturer_price, rand_sale_price, rand_date))
#
#         remaining_quantity = item['quantity'] - quantity
#         item_query = f"UPDATE `items` SET `quantity`=%s WHERE `id`=%s"
#         c.execute(item_query, (remaining_quantity, item_id))
#
#         conn.commit()
#
#
# def most_popular_item():
#     query = """
#     SELECT
#         item_id,
#         title,
#         SUM(p.quantity) AS agg_quantity
#     FROM
#         `payments` p
#     JOIN `items` i ON
#         i.id = p.item_id
#     GROUP BY
#         item_id
#     ORDER BY
#         agg_quantity
#     DESC
#     LIMIT 1
#     """
#     c.execute(query)
#     item = c.fetchone()
#     print(f"Daugiausia parduota šios prekės: {(item[1])}. Kiekis: {item[2]} vnt.")
#
#
# def most_profitable_item():
#     query = """
#     SELECT
#         i.id AS item_id,
#         i.title,
#         SUM(
#             (
#                 p.sale_price_per_unit - p.manufacturer_price
#             ) * p.quantity
#         ) AS profit_per_item
#     FROM
#         payments p
#     JOIN items i ON
#         i.id = p.item_id
#     GROUP BY
#         p.item_id
#     ORDER BY
#         profit_per_item
#     DESC
#     LIMIT 1
#     """
#     c.execute(query)
#     item = c.fetchone()
#     print(f"Daugiausia pelno sugeneravusi prekė: {(item[1])}. Pelnas: {item[2]} Eur")
#
#
# def sales_report():
#     year = int(input("Pasirinkite ataskaitinius metus (2022-2024): "))
#     year_start = datetime.date(year=year, month=1, day=1)
#     year_end = datetime.date(year=year+1, month=1, day=1)
#
#     query = """
#     SELECT
#         DATE_FORMAT(created_at, "%Y-%m") AS month,
#         SUM(quantity) AS total_quantity,
#         SUM(quantity * sale_price_per_unit) AS total_sales,
#         SUM(
#             (
#                 sale_price_per_unit - manufacturer_price
#             ) * quantity
#         ) AS profits
#     FROM
#         `payments`
#     WHERE
#         created_at BETWEEN DATE(%s) AND DATE(%s)
#     GROUP BY
#         month
#     """
#     c.execute(query, (year_start, year_end))
#     items = c.fetchall()
#     print("Data    Parduota prekių    pajamos    pelnas")
#     for item in items:
#         print(f"{item[0]}       {item[1]}            {item[2]}       {item[3]}")
#
#
# def inventory_cost():
#     query = "SELECT SUM(quantity * manufacturer_price) FROM `items`"
#     c.execute(query)
#     res = c.fetchone()
#     print(f"Įšaldytų atsargų savikaina yra: {res[0]} Eur")
#
# def inventory_at_market_prices():
#     query = "SELECT SUM(quantity * sale_price) FROM `items`"
#     c.execute(query)
#     res = c.fetchone()
#     print(f"Atsargų vertė rinkos kainomis yra: {res[0]} Eur")
#
#
# def expected_profits():
#     query = "SELECT SUM(quantity * (sale_price - manufacturer_price)) FROM `items`"
#     c.execute(query)
#     res = c.fetchone()
#     print(f"Prognozuojamas pelnas išpardavus atsargas: {res[0]} Eur")
#
#
# while True:
#     print_info()
#     choice = input()
#
#     match choice:
#         case '1':
#             print_items()
#         case '2':
#             add_item()
#         case '3':
#             print_items()
#             edit_item()
#         case '4':
#             delete_item()
#         case '5':
#             print_items()
#             buy_item()
#         case '6':
#             exit()
#         # case '6':
#         #     most_popular_item()
#         # case '7':
#         #     most_profitable_item()
#         # case '8':
#         #     sales_report()
#         # case '9':
#         #     inventory_cost()
#         # case '10':
#         #     inventory_at_market_prices()
#         # case '11':
#         #     expected_profits()
#         # case '12':
#         #     exit()