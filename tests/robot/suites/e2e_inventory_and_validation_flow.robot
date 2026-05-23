*** Settings ***
Documentation     E2E workflow for validating inventory and referential integrity rules.
Library           DataDriver    file=${CURDIR}/../data/inventory_validation_flow.csv    encoding=utf-8
Resource          ../resources/api.resource
Suite Setup       Prepare API Session
Suite Teardown    Close API Session
Test Template     Run Inventory Validation Workflow

*** Test Cases ***
Inventory validation workflow from CSV

*** Keywords ***
Run Inventory Validation Workflow
    [Arguments]    ${category_name}    ${category_description}    ${customer_first_name}    ${customer_last_name}    ${customer_email}    ${customer_phone}    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${order_date}    ${order_quantity}    ${overstock_quantity}

    &{category_payload}=    Create Dictionary
    ...    name=${category_name}
    ...    description=${category_description}
    ${category}=    Create Resource    /categories    &{category_payload}
    ${category_id}=    Get From Dictionary    ${category}    id

    &{customer_payload}=    Create Dictionary
    ...    first_name=${customer_first_name}
    ...    last_name=${customer_last_name}
    ...    email=${customer_email}
    ...    phone=${customer_phone}
    ${customer}=    Create Resource    /customers    &{customer_payload}
    ${customer_id}=    Get From Dictionary    ${customer}    id

    &{product_payload}=    Create Dictionary
    ...    name=${product_name}
    ...    description=${product_description}
    ...    price=${product_price}
    ...    stock_quantity=${product_stock}
    ...    category_id=${category_id}
    ${product}=    Create Resource    /products    &{product_payload}
    ${product_id}=    Get From Dictionary    ${product}    id

    &{order_payload}=    Create Dictionary
    ...    customer_id=${customer_id}
    ...    order_date=${order_date}
    ...    total_amount=0
    ...    status=Pending
    ${order}=    Create Resource    /orders    &{order_payload}
    ${order_id}=    Get From Dictionary    ${order}    id

    &{order_item_payload}=    Create Dictionary
    ...    order_id=${order_id}
    ...    product_id=${product_id}
    ...    quantity=${order_quantity}
    ...    price=${product_price}
    ${order_item}=    Create Resource    /order-items    &{order_item_payload}
    ${order_item_id}=    Get From Dictionary    ${order_item}    id

    &{oversized_order_item_payload}=    Create Dictionary
    ...    order_id=${order_id}
    ...    product_id=${product_id}
    ...    quantity=${overstock_quantity}
    ...    price=${product_price}
    Create Resource Expecting Conflict    /order-items    &{oversized_order_item_payload}

    Delete Resource Expecting Conflict    /products    ${product_id}
    Delete Resource Expecting Conflict    /customers    ${customer_id}

    Delete Resource    /order-items    ${order_item_id}
    Delete Resource    /orders    ${order_id}
    Delete Resource    /products    ${product_id}
    Delete Resource    /customers    ${customer_id}
    Delete Resource    /categories    ${category_id}
