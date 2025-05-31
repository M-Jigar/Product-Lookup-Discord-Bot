import httpx
import json
import random

baseURL = "https://api.escuelajs.co/api/v1/products/"

prod_id = "32"
prod_name = "Handmade Fresh Table"

prod_input = prod_id

def verify_and_create_endURL(prod):

    """
    verifies the input whether its integer (id) or string (slug)
    and creates an appropriate end URL.
    """

    if prod.isdigit():
        prod = int(prod)
        endURL = f"{baseURL}{prod}"
    else:
        slug = prod.lower().strip().replace(" ", "-")
        endURL = f"{baseURL}slug/{slug}"

    return endURL


def error_handler(response) -> dict:

    msg = {
        400: "Product not found.",
        500: "Server error at API."
        }

    if response.status_code == 200:
        return response.json()

    elif response.status_code in msg:
        return {"error_message": msg[response.status_code]}
    
    else:
        return {"error_message": "Unmentioned Error"}


def get_prod_data(prod) -> dict:

    endURL = verify_and_create_endURL(prod)

    response = httpx.get(endURL)

    prod_data = error_handler(response)         # This is dict type ---- I have used .json() in error handler itself.

    response_json_pretty = json.dumps(prod_data, indent=4)  # This is str type

    """with open("prod_dump.json", "w") as f:
        f. write(response_json_pretty)"""

    return prod_data

def get_random_prod() -> dict:

    response = httpx.get("https://api.escuelajs.co/api/v1/products").json()

    prod_id_list = []
    for x in response:
        prod_id_list.append(x["id"])

    rand_id = str(random.choice(prod_id_list))

    rand_prod_data = get_prod_data(rand_id)

    return rand_prod_data

def get_cat_data() -> list:

    response = httpx.get("https://api.escuelajs.co/api/v1/categories").json()

    cat_name_list = []

    for x in response[:5]:      #limiting th list to only 5 items, lazy dogding an error when more than 10 items in the list, cuz no emoji after '10'.
        cat_name = x["name"]
        cat_name_list.append(cat_name)

    
    return cat_name_list

def get_prods_by_cat(cat_id) -> list:

    response = httpx.get(f"https://api.escuelajs.co/api/v1/categories/{cat_id}/products").json()

    return response