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


### 4. History
Get the previous orders of the user

* GET URL: http://lannister-api.elasticbeanstalk.com/tyrion/history
* Parameters:
    1. `email`: The email address of the registered user
    2. `vendor_id`: The usual
* Result: A list of previous orders, please check url


### 5. Feedback
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
