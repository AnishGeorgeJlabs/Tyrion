# Database design for the menus
This documentation describes the complete design of the MongoDB based database for _Tyrion_. 

### Key conventions
* All our database keys are lower case words separated by _ (underscore)
* Keys ending in `_id` are primary keys and have a uniqueness constraint attached (the exception being `vendor_id`).
These are usually integers.
* The `vendor_id` key is special in the sense that the whole database revolves around vendors and this key is used to
separate data for different vendors. This key is present in each object of every collection.
* Keys ending in `_fk` are foreign keys which have a related `*_id` key in another collection. Usually, the name of the
foreign collection will be preceded by the `_fk` as in `template_customize_fk` means a foreign key on the _template_customize_ collection.

## Top to bottom design of the Menu (API view)
The following is the complete final design of the menu as retrieved by the API

#### Base Menu
```JSON
{
  "vendor_id": 1,
  "version": 1,
  "menu": [ <a list of categories> ]
}
```

#### - Category
```JSON
{
  "category": "Name of the category",
  "desc": "Optional description for category",
  "items": [ <a list of items> ]
}
```

#### -- Item
```JSON
{
  "name": "Name of item",
  "desc": "Description",
  "simple": <Boolean indicating whether there is a price field or 
            does it have multiple prices for various sizes>,
  "size": <available only when simple is false> [ <a list of size components> ],
  "price": <available only when simple is true> <An integer>,
  "custom": <optional> [ <a list of customization categories> ],
  "tags": <optional> [ <a list of tags> ]
}
```
The size component being ```{ "name": "size name", "price": <integer> }```

#### --- Customization Category
```JSON
{
  "name": "Name of the customization, like Crust selection",
  "type": "One of the many specific types that our apps recognise, 
          currently, one of multi, single, optional",
  "options": [ <a list of customization options> ]
}
```
The customization option being ```{"name": "option name", "price": <integer, additional charge over base price>, "tags": <a list of tags>}```

## Database Design
### The `menu` collection
This collection contains the main structure of the menu and forms the core of the data. 

**Indexes**
* `vendor_id`: unique

The structure of the menu is uniform till the item nest level. i.e. it will always have the following base structure:
```JSON
{
  "vendor_id": <int>,
  "version": <int>,
  "menu": [{
    "category": "name of cat",
    "items": [ {...} ]
  }]
}
```

The item may be in one of two forms:
1. A completed item as described in the API design section
2. An incomplete item having references to templates.

The second form is the most scalable. Here, the item looks like
```JSON
{
  "name": "Item name",
  "template_size_fk": "The size template",
  "template_customize_fk": "Teh customization template",
  "desc": "Description",
  "any additional keys": "giving additional metadeta at item level"
}
```
* The `template_size_fk` is optional, you may have an embedded `size` object as described previously or you may have a 
`price` key which makes the item a simple item.
* The `template_customize_fk` is again optional. You may have an embedded `custom` object or you may omit this key so
that the item may not have any kind of customization available.

### The `template_size` collection
This collection stores named templates for size selection of items. Size options are by default interpreted as single selection at app side.

**Indexes**
* `template_id`: unique
* `template_id` & `vendor_id`: sorted

The base format is
```JSON
{
  "template_id": <int>,
  "vendor_id": <int>,
  "name": "Optional name, only for database clarity",
  "size": [{
    "name": "Size name",
    "price": <int>
  }]
}
```

### The `template_customize` collection
This collection sotres named customization templates for items in menu.
Each template actually stores a customization list which contains different categories of customizations, each with its
own options.

**Indexes**
* `template_id`: unique
* `template_id` & `vendor_id`: sorted

The base format is
```JSON
{
  "template_id": <int>,
  "vendor_id": <int>
  "name": "Optional name for database clarity",
  "options": [ <a list of cutomization categories> ]
}
```

#### Customization category
A category may be a complete object as described in the design or it may be an incomplete object containing a reference
to a category using the `customize_fk` key which will point to a customization category stored in the **customize** collection.

```JSON
{
  "customize_fk": <int>,
  "additional key": "Metadata which is specific to this category 
                      but in the context of this particular template"
}
```

Usually, we have support for `hard_limit` or `soft_limit` (check the miscellaneous section) as additional keys which cannot be embedded in the customization
collection as these may need to be changed per item or category of the menu.

### The `customize` collection
This collection stores customization categories. For example, a category for pizza crusts, another for veg toppings etc.

**Indexes**
* `customize_id`: unique
* `customize_id` & `vendor_id`: sorted

The base base format is
```JSON
{
  "name": "Name of the customization category",
  "type": "One of the many customization types supported. 
            check miscellaneous section for details",
  "options": [{
    "name": "Option name",
    "price": <int, the additional price over the base price of the item>,
    "tags": [<a list of tags>]
  }]
}
```

## Miscellaneous
#### Tags
Tags are markers used to describe food quality and style. These are added as `"tags": [ <list of tags> ]` in the valid
database objects. Various elements in the menu may have tags. These are:
* items
* customization category options

The currently supported tags and their means are:

| tag | Meaning |
| ---:|:------- |
| veg | Vegetarian food |
| nveg| Non Vegetarian food |
| rec | Recommended, restaurant special |
| spc | Spicy |
| espc | Extra spicy |


#### Customization types and modifiers
These types are part of the customization categories (in the `customize` collection). 
Currently the system supports the following types

| type | Behaviour |
| ---- | ------- |
| single | One and only one option may be selected from the given options |
| multi | Multiple options may be selected, but there should be atleast one selection |
| optional | Multiple options may be selected, nothing may be selected as well. For extras |

Several modifiers to these behaviour may be added (as key value pairs) either in the customization category themselves
(making it restrictive to that category throughout) or to the customization objects inside the templates (which hold
references to the customization categories). In either case, the end result data will contain these modifiers inside the
customization categories like so `{ "soft_limit": 2, "name": "toppings", "options": [...] }`

The various modifiers are given below

| Modifier | Acceptable values | Behaviour 
| -------- | ----------------- | --------- 
| hard_limit | integer x > 0 and > soft_limit (if present) | Maximum number of selections for the category |
| soft_limit | integer x > 0 | The number of selection up to the soft_limit will incur **no additional charges** on the base price, but further selection will add their respective charges |
