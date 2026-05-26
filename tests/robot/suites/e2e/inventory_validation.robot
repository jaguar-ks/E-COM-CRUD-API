*** Settings ***
Documentation     E2E workflow for validating inventory and referential integrity rules.
Library           DataDriver    file=${CURDIR}/../../data/inventory_validation_flow.csv    encoding=utf-8
Resource          ../../resources/api.resource
Suite Setup       Prepare API Session
Suite Teardown    Close API Session
Test Template     Run Inventory Validation Workflow

*** Test Cases ***
Inventory validation workflow from CSV - ${product_name} - ${customer_email}

*** Keywords ***
Run Inventory Validation Workflow
    [Arguments]    ${category_name}    ${category_description}    ${customer_first_name}    ${customer_last_name}    ${customer_email}    ${customer_phone}    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${order_date}    ${order_quantity}    ${overstock_quantity}

    ${category}    ${category_id}=    Create Category    ${category_name}    ${category_description}
    ${customer}    ${customer_id}=    Create Customer    ${customer_first_name}    ${customer_last_name}    ${customer_email}    ${customer_phone}
    ${product_summary}=    Create Product    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${category_id}
    ${product}=    Get From Dictionary    ${product_summary}    body
    ${product_id}=    Get From Dictionary    ${product_summary}    id
    ${product_price}=    Get From Dictionary    ${product_summary}    price
    ${product_stock}=    Get From Dictionary    ${product_summary}    stock
    ${order}    ${order_id}=    Create Order    ${customer_id}    ${order_date}
    ${order_item}    ${order_item_id}=    Create Order Item    ${order_id}    ${product_id}    ${order_quantity}    ${product_price}

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
