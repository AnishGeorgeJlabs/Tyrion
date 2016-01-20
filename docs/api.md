# Api Documentation for Tyrion

### Notes:
1. All APIs return JSON.
2. The `success` key determines whether the call was successfully processed or not.
3. The `data` key will contain the result of the operation
4. Host domain is [http://lannister-api.elasticbeanstalk.com/tyrion](http://lannister-api.elasticbeanstalk.com/tyrion)


### 1. Menu
Get the complete menu from the system

* GET URL: http://lannister-api.elasticbeanstalk.com/tyrion/menu
* Parameters:
    1. `vendor_id`: The integer vendor id
  
* Returns: The complete menu structure, check url
* Menu structure simplified:
```JSON
{
  "documentation": {
    "tags_docs": "These are optional boolean tags that may be associated with a menu item and/or its toppings",
    "tags": [ "veg", "nveg", "sp", "esp", "rec", "new" ]
  },
  "menu": [
    {
      "category": "Smoking Hot Pizzas",
      "items": [
        {
          "name": "Mexican Chille",
          "tags": ["sp"],
          "simple": true,
          "price": 520
        },
        {
          "name": "Some other simple",
          "tags": ["sp"],
          "simple": true,
          "size": [
            { "name": "Small", "price": 150 },
            { "name": "Medium", "price": 200 },
            { "name": "Large", "price": 250 }
          ]
        },
        {
          "name": "Supreme Non-veg",
          "tags": ["nveg"],
          "simple": false,
          "size": [
            { "name": "Small", "price": 150 },
            { "name": "Medium", "price": 200 },
            { "name": "Large", "price": 250 }
          ],
          "custom": [
            {
              "name": "Base",
              "type": "single",
              "option": [
                { "name": "Classic Pan", "price": 0 },
                { "name": "Thin Crust", "price": 50 },
                { "name": "Deep Crust", "price": 50 }
              ]
            },
            {
              "name": "Toppings",
              "type": "multi",
              "soft_limit": 3,
              "hard_limit": 5,
              "option": [
                { "name": "Ham", "price": 10, "tags": ["nveg"] },
                { "name": "Chicken", "price": 10, "tags": ["nveg"]},
                { "name": "Jalepeno", "price": 10, "tags": ["veg", "sp"]},
                { "name": "Pork", "price": 10, "tags": ["nveg", "new"]}
              ]
            },
            {
              "name": "Extras",
              "type": "optional",
              "option": [
                { "name": "toppings non-veg", "price": 20, "tags": ["nveg"] },
                { "name": "cheese", "price": 20}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```


### 2. Version check of menu
Check to see whether you have the latest menu version with you

* GET URL: http://lannister-api.elasticbeanstalk.com/tyrion/menu/check_version
* Paramters:
    1. `vendor_id`: The usual
    2. `version`: An integral version number, the menu of which you currently posses
  
* Returns: Boolean, true if your version is the current else false


### 3. Place Order
Call to place the actual order

* POST URL: http://lannister-api.elasticbeanstalk.com/tyrion/order
* JSON data:
```JSON
{
  "vendor_id": 1,
  "email": "email address",
  "phone": "phone, number",
  "name": "Anish George",
  "address": "Address full",
  "area": "Short area name",
  "order": [
    {
      "category": "index",
      "item": "index",
      "qty": "Quantity, defaults to 1",
      "size": "index, optional",
      "custom": [
        [], [1,5,6], []
      ]
    },
    {
      "category": 1
    }
  ]
}
```
* Result: An object `{ price: <total price>, order_number: <the generated order number> }`


### 4. History
Get all the orders of the given user

* GET URL: http://lannister-api.elasticbeanstalk.com/tyrion/history
* Parameters:
    1. `email`: The email address of the registered user
    2. `vendor_id`: The usual
    3. `status`: Comma delimited set of status' for the orders in the result list, optional, defaults to any status
* Result: A list of previous orders, please check url

The status one or more of the following values

1. placed
2. accepted
3. cancelled
4. delayed
5. ready
6. delivered

Historical orders can have status `cancelled` or `delivered` only. All the other status' signify an active order.
So to get order history, use parameter `status=cancelled,delivered` and to get current order, use parameter
`status=placed,accepted,delayed,ready`

### 5. Order details
Get the complete order details of a given order

* GET URL: http://lannister-api.elasticbeanstalk.com/tyrion/details
* Parameters:
    1. `vendor_id`: the usual
    2. `order_number`: The order number for the required order
* Result: the complete order details, check url

### 6. Feedback
Post a feedback which will be mailed by the system to the given vendor

* POST URL: http://lannister-api.elasticbeanstalk.com/tyrion/feedback
* JSON data:
```JSON
{
  "email": "registered user email",
  "phone": "registered phone number",
  "vendor_id": <int vendor id>,
  "subject": "Subject of mail, is optional",
  "body": "Body of the mail"
}
```

### 7. Address
Managing user addresses

URL: http://lannister-api.elasticbeanstalk.com/tyrion/address

#### 7.1 GET
Returns a list of all the addresses of the given user

* Parameters:
    1. `vendor_id`: the usual
    2. `email`: email of the user
* Result: An array of user addresses. Error if user doesn't exist

#### 7.2 POST
Add a new address for the user

* JSON data:
```JSON
{
  "email": "email address of user",
  "vendor_id": <int vendor id>,
  "address": <full address object>
}
```
* Result: Success. If a user does not exists, it is created


### 8. Areas
Get a list of all the areas you vendor delivers to

* URL: http://lannister-api.elasticbeanstalk.com/tyrion/areas
* Parameters:
    1. `vendor_id`: the usual
* Result: An array of areas
