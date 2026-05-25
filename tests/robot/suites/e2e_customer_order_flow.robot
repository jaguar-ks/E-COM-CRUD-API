*** Settings ***
Documentation     E2E workflow for placing an order against seeded demo data.
Library           DataDriver    file=${CURDIR}/../data/customer_order_flow.csv    encoding=utf-8
Resource          ../resources/api.resource
Suite Setup       Prepare API Session
Suite Teardown    Close API Session
Test Template     Customer Order Workflow

*** Test Cases ***
Customer order workflow from CSV

*** Keywords ***
Customer Order Workflow
    [Arguments]    ${customer_email}    ${category_name}    ${category_description}    ${product_name}    ${product_description}    ${product_price}    ${product_stock}    ${order_quantity}    ${order_date}    ${expected_order_status}

    ${customer}=    Find Item By Field    /customers    email    ${customer_email}
    &{category_payload}=    Create Dictionary
    ...    name=${category_name}
    ...    description=${category_description}
    ${category}=    Create Resource    /categories    &{category_payload}
    ${category_id}=    Get From Dictionary    ${category}    id

    &{product_payload}=    Create Dictionary
    ...    name=${product_name}
    ...    description=${product_description}
    ...    price=${product_price}
    ...    stock_quantity=${product_stock}
    ...    category_id=${category_id}
    ${product_before}=    Create Resource    /products    &{product_payload}

    ${customer_id}=    Get From Dictionary    ${customer}    id
    ${product_id}=    Get From Dictionary    ${product_before}    id
    ${product_stock_before}=    Get From Dictionary    ${product_before}    stock_quantity
    ${product_price}=    Get From Dictionary    ${product_before}    price

    &{order_payload}=    Create Dictionary
    ...    customer_id=${customer_id}
    ...    order_date=${order_date}
    ...    total_amount=0
    ...    status=${expected_order_status}
    ${order}=    Create Resource    /orders    &{order_payload}
    ${order_id}=    Get From Dictionary    ${order}    id

    &{order_item_payload}=    Create Dictionary
    ...    order_id=${order_id}
    ...    product_id=${product_id}
    ...    quantity=${order_quantity}
    ...    price=${product_price}
    ${order_item}=    Create Resource    /order-items    &{order_item_payload}
    ${order_item_id}=    Get From Dictionary    ${order_item}    id

    ${order_after}=    Get Resource By Id    /orders    ${order_id}
    ${product_after}=    Get Resource By Id    /products    ${product_id}

    ${order_total}=    Get From Dictionary    ${order_after}    total_amount
    ${order_status}=    Get From Dictionary    ${order_after}    status
    ${product_stock_after}=    Get From Dictionary    ${product_after}    stock_quantity

    ${expected_total}=    Evaluate    int(${product_price}) * int(${order_quantity})
    Assert Equal Integer Fields    ${order_after}    total_amount    ${expected_total}
    Should Be Equal    ${order_status}    ${expected_order_status}
    Assert Integer Difference    ${product_stock_before}    ${product_stock_after}    ${order_quantity}

    Delete Resource    /order-items    ${order_item_id}
    Delete Resource    /orders    ${order_id}
    Delete Resource    /products    ${product_id}
    Delete Resource    /categories    ${category_id}
