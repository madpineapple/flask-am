import requests
import urllib

class DotNetAPI:
  def __init__(self, base_url="http://localhost:5230"):
    self.base_url = base_url

  def get_item_total(self, item_name:str):
    try:
      encoded_name = urllib.parse.quote(item_name)
      response = requests.get(f"{self.base_url}/Product/countinfo/{encoded_name}")
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
  def get_item_by_lot(self, item_name: str,lot_num: str):
    try:
      encoded_name = urllib.parse.quote(item_name)
      url = f"{self.base_url}/Product/lotInfo/{encoded_name}"
      response = requests.get(url, params={"product_lot_number": lot_num})
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
  def get_item_by_loc(self, item_name: str, location: str):
    try:
      encoded_name = urllib.parse.quote(item_name)
      url = f"{self.base_url}/Product/locationInfo/{encoded_name}"
      response = requests.get(url, params={"product_location": location})
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
  def get_item_by_expr(self, item_name: str, expiry_query ):
    try:
      encoded_name = urllib.parse.quote(item_name)
      url = f"{self.base_url}/Product/expiryInfo/{encoded_name}"
      response = requests.get(url, params={"expiry_info": expiry_query})
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
  def get_item_rows(self, item_name: str):
    try:
      encoded_name = urllib.parse.quote(item_name)
      response = requests.get(f"{self.base_url}/Product/info/{encoded_name}")
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}